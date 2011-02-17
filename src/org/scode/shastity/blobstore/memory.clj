(ns org.scode.shastity.blobstore.memory
  (:require [org.scode.shastity.blobstore :as blobstore]))

(deftype MemoryStore [contents]
  blobstore/BlobStore
  (put-blob [store name value] (dosync (commute contents conj [name value])))
  (get-blob [store name] (get @contents name))
  (delete-blob [store name] (dosync (commute contents dissoc name)))
  (list-blobs [store] (keys @contents)))


