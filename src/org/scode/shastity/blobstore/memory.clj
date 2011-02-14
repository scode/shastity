(ns org.scode.shastity.blobstore.memory
  (:require [org.scode.shastity.blobstore :as blobstore]))

(deftype MemoryStore []
  blobstore/BlobStore
  (put-blob [store name vaule] nil)
  (get-blob [store name] nil)
  (delete-blob [store name] nil)
  (list-blobs [store] nil))

