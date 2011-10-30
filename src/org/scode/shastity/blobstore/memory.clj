(ns org.scode.shastity.blobstore.memory
  (:require [org.scode.shastity.blobstore :as blobstore])
  (:import [org.scode.shastity.java Bytes]))

(deftype MemoryStore [contents]
  ;; Stores everything in a map. Being primarily intended for testing purposes, it additionall contains
  ;; sanity checks on input.
  blobstore/BlobStore
  (put-blob [store name value]
    (assert (= (.getClass name) String))
    (assert (not (.isEmpty name)))
    (assert (= (.getClass value) Bytes))
    (dosync (commute contents conj [name value])))
  (put-blob-if-absent [store name value]
    (assert (= (.getClass name) String))
    (assert (not (.isEmpty name)))
    (assert (= (.getClass value) Bytes))
    (dosync (if (not (blobstore/has-blob store name)) (blobstore/put-blob store name value))))
  (has-blob [store name]
    (assert (= (.getClass name) String))
    (assert (not (.isEmpty name)))
    (not (nil? (get @contents name))))
  (get-blob [store name]
    (assert (= (.getClass name) String))
    (assert (not (.isEmpty name)))
    (get @contents name))
  (delete-blob [store name]
    (assert (= (.getClass name) String))
    (assert (not (.isEmpty name)))
    (dosync (commute contents dissoc name)))
  (list-blobs [store] (keys @contents)))
