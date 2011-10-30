(ns org.scode.shastity.manifest
  (:require [org.scode.shastity.blobstore :as blobstore])
  (:import [org.scode.shastity.java Bytes]))

(defprotocol ManifestWriter
  ""
  (add-object [manifest pathname metadata hashes]
    "Add the given pathname (must be unique) to the manifest, associating the given meta-data and seqable of hashes.")
  (freeze [manifest]
    "Finalize the manifest, producing contentes ready to be uploaded and preventing further paths to be added.")
  (upload [manifest store name]
    "Upload the manifest to the given blob store under the given name."))

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

;; TODO: Replace with manifest writer using a tempfile and sorting on finalize.
(deftype InMemoryManifestWriter [objects finalized]
  ManifestWriter
  (add-object [manifest pathname metadata hashes]
    (dosync
      (assert (not @finalized))
      (alter objects conj [pathname metadata hashes])))
  (freeze [manifest]
    (dosync
      (ref-set finalized true)))
  (upload [manifest store name]
    (let [sorted-objects (sort (comparator #(first %1) @objects))
          string-writer (java.io.StringWriter.)]
      (doseq [[pathname metadata hashes] sorted-objects]
        (doto string-writer
          (.write (encode pathname))
          (.write " ")
          (.write (encode (str metadata)))
          (.write " "))
        (doseq [hash hashes]
          (doto string-writer
            (.write hash)
            (.write " ")))
        (.write string-writer "\n"))
      (blobstore/put-blob store name (Bytes/encode (.toString string-writer))))))

(defn create-manifest-writer []
  (.InMemoryManifestWriter (ref #{}) (ref false)))
