(ns org.scode.shastity.manifest
  (:require [org.scode.shastity.blobstore :as blobstore]
            [clojure.string :as string]
            [clojure.java.io :as jio])
  (:import [org.scode.shastity.java Bytes]))

; Compare pathname only.
(defn manifest-entry-comparator [a b]
  (compare (first a) (first b)))

(defprotocol ManifestWriter
  "A thin abstraction for ceating a manifest. We do not want to use a native clojure data structure because we
  do not want to keep an entire manifest in memory. The operations we want to do are essentially to incrementally add
  to one, and to stream through a manifest (in sorted order).

  In a future clojure, maybe we can use streams for this. For now, I have this. Better suggestions welcome, as
  I am not sure what would be most idiomatic.

  The distinction between freeze and upload is there because it is presume that there may be work involved that is
  locally performance-bound (e.g, doing a merge-sort of data on disk) and it is nice to schedule that separately
  from the upload which is backend bound (presumably).

  For reading a manifest, a ManifestReader is used."
  (add-object [mwriter pathname metadata hashes]
    "Add the given pathname (must be unique) to the manifest, associating the given meta-data and seqable of hashes.")
  (freeze [mwriter]
    "Finalize the manifest, producing contentes ready to be uploaded and preventing further paths to be added.")
  (upload [mwriter store name]
    "Upload the manifest to the given blob store under the given name."))

(defprotocol ManifestReader
  "Counterpart of ManifestWrite. See its documentation for general rationale."
  (get-objects [mreader store name]
    "Get sequence (presumably either small or lazy) of objets in the manifest, in sorter (on name) order. "))

(def ^:private ^:dynamic *character-whitelist* (into #{}
                                                 (str
                                                   "abcdefghijklmnopqrstuvxyz"
                                                   "ABCDEFGHIJKLMNOPQRSTUVXYZ"
                                                   "0123456789"
                                                   "/-._~")))
(defn hex-byte [byte] ;todo private
  (let [int-value (let [raw-int (int byte)]
                    (if (< raw-int 0)
                      (+ 127 1 (- raw-int -128))
                      raw-int))]
    (assert (<= int-value 255))
    (format "%02x" int-value)))

(defn unhex-byte [hex1 hex2]
  (.byteValue (bit-or (bit-shift-left (Character/digit hex1 16) 4) (Character/digit hex2 16))))

(defn escape [chr] ;todo private
  "chr -> string"
  (let [bytes (.getBytes (str chr) "UTF-8")]
    (apply str (map #(str "%" (hex-byte %1)) bytes))))

(defn encode [s] ;todo private
  "Encode string for safe use in a space separated manifest. All whitespace plus various non-readable stuff is encoded."
  (apply str (map #(if (contains? *character-whitelist* %1) %1 (escape %1)) s)))

(defn decode [s] ;todo private
  "Inverse of encode."
  (let [out (java.io.ByteArrayOutputStream.)]
    (loop [remainder (seq s)]
      (if (not (seq remainder))
        nil
        (let [next-char (first remainder)]
          (if (= next-char \%)
            (let [hex1 (nth remainder 1)
                  hex2 (nth remainder 2)]
              (if (or (nil? hex1) (nil? hex2))
                (throw (RuntimeException. "pre-mature end-of-string after % - not encoded correctly")) ;; todo cleaner exception
                (do
                  (.write out (int (unhex-byte hex1 hex2)))
                  (recur (rest (rest (rest remainder)))))))
            (do
              (let [int-val (int next-char)]
                (assert (<= int-val 127)) ; todo not assert, broken input
                (.write out int-val))
              (recur (rest remainder)))))))
    (String. (.toByteArray out) "UTF-8")))

(defn encode-object [[pathname metadata hashes]] ; todo private
  (let [string-writer (java.io.StringWriter.)]
    (doto string-writer
      (.write (encode pathname))
      (.write " ")
      (.write (encode (str metadata)))
      (.write " "))
    (doseq [hash hashes]
      (doto string-writer
        (.write hash)
        (.write " ")))
    (.toString string-writer)))

(defn decode-object [str] ; todo private
  (let [[name meta & hashes] (string/split str #" ")]
    (if (or (nil? name) (nil? meta))
      (throw (RuntimeException. (str "missing meta and maybe name in manifest line: " str)))
      (let [dec-name (decode name)
            dec-meta (read-string (decode meta))]
        ;; todo: validate that hashes are appropriate hexdigests
        [dec-name dec-meta (if (seq? hashes) hashes [])]))))

;; TODO: Replace with manifest writer using a tempfile and sorting on finalize.
(deftype InMemoryManifestWriter [objects finalized]
  ManifestWriter
  (add-object [mwriter pathname metadata hashes]
    (dosync
      (assert (not @finalized))
      (alter objects conj [pathname metadata hashes])))
  (freeze [mwriter]
    (dosync
      (ref-set finalized true)))
  (upload [mwriter store name]
    (let [string-writer (java.io.StringWriter.)]
      (doseq [[pathname metadata hashes] @objects]
        (.write string-writer (encode-object [pathname metadata hashes]))
        (.write string-writer "\n"))
      (blobstore/put-blob store name (Bytes/encode (.toString string-writer))))))

(deftype InMemoryManifestReader []
  ManifestReader
  (get-objects [mreader store name]
    (let [manifest-blob (blobstore/get-blob store name)
          manifest-string (.decode manifest-blob)
          rin (jio/reader (java.io.StringReader. manifest-string))]
      (loop [objects (sorted-set-by manifest-entry-comparator)]
        (let [line (.readLine rin)]
          (if (nil? line)
            (seq objects)
            (recur (conj objects (decode-object line)))))))))

(defn create-manifest-writer []
  (InMemoryManifestWriter. (ref (sorted-set-by manifest-entry-comparator)) (ref false)))

(defn create-manifest-reader []
  (InMemoryManifestReader.))

