(ns org.scode.shastity.blobstore)

(defprotocol BlobStore
  "Interface to a blob store, offering basic put/get/delete/list
  functionality. Consistency semantics are intended to be roughly
  equivalent to S3 style eventual consistency.

  It is specifically tailored to the shastity use case for simplicity. In particular, the blob management
  always assumes reasonably sized in-memory blobs; only list-blobs is designed to support streaming."
  (put-blob [store name value] "Put a blob (Bytes) into the store")
  (get-blob [store name] "Get a blob (Bytes) from the store; nil if non-existent")
  (has-blob [store name] "Return whether the blob exists in the store")
  (delete-blob [store name] "Delete a blob (Bytes) from the store (do nothing if it does not exist)")
  (list-blobs [store]
    "Return seqable of all names in the store - callers should be mindful that the store may keep
    resources active until the seqable is consumed. This also implies that for thread-safety, the store
    may not be re-used until the seqable has been consumed."))

