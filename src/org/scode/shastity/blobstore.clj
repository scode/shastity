(ns org.scode.shastity.blobstore)

(defprotocol BlobStore
  "Interface to a blob store, offering basic put/get/delete/list
  functionality. Consistency semantics are intended to be roughly
  equivalent to S3 style eventual consistency."
  (put-blob [store name value] "Put a blob (Bytes) into the store")
  (get-blob [store name] "Get a blob (Bytes) from the store; nil if non-existent")
  (has-blob [store name] "Return whether the blob exists in the store")
  (delete-blob [store name] "Delete a blob (Bytes) from the store (do nothing if it does not exist)")
  (list-blobs [store] "Return seqable of all names in the store"))

