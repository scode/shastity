(ns org.scode.shastity.manifest
  (:require [org.scode.shastity.blobstore :as blobstore]
            [clojure.string :as string]
            [clojure.java.io :as jio])
  (:import [org.scode.shastity.java Bytes]
           [java.nio.file Path]))

; Whitelist of characters not encoded when they appear in file names. This whitelist cannot
; be changed without altering the on-disk contents of meta-data. Changing it will not break
; compatibility, but will defeat de-duplication with respect to old metadata.
(def ^:private ^:dynamic *character-whitelist* (into #{}
                                                 (str
                                                   "abcdefghijklmnopqrstuvxyz"
                                                   "ABCDEFGHIJKLMNOPQRSTUVXYZ"
                                                   "0123456789"
                                                   "-._~")))
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

