(ns org.scode.shastity.blobstore)

(defprotocol BlobStore
  "Interface to a blob store, offering basic put/get/delete/list
  functionality. Consistency semantics are intended to be roughly
  equivalent to S3 style eventual consistency."
  (put-blob [store name value] "Put a blob (byte array) into the store")
  (get-blob [store name] "Get a blob (byte array) from the store; nil if non-existent")
  (delete-blob [store name] "Delete a blob (byte array) from the store")
  (list-blobs [store] "List all names in the store"))

