(ns org.scode.shastity.blobstore.s3
  (:require [org.scode.shastity.blobstore :as blobstore])
  (:import [org.scode.shastity.java Bytes]
           [com.amazonaws.services.s3.model ObjectMetadata ListObjectsRequest AmazonS3Exception]))

(deftype S3Store [s3-client bucket-name path]
  ;; TODO: prefix vs. path; validate trailing / if need be
  ;; TODO: list-blobs should stream
  ;; TODO: existence check triggers spurious logging by the AWS SDK :(
  blobstore/BlobStore
  (put-blob [store name value] (let [meta-data (ObjectMetadata.)]
                                 (.setContentLength meta-data (.length value))
                                 (.putObject s3-client bucket-name (str path name) (.getInputStream value) meta-data)))
  (has-blob [store name] (try
                           (let [meta-data (.getObjectMetadata s3-client bucket-name (str path name))]
                             true)
                           (catch AmazonS3Exception e (if (= 404 (.getStatusCode e))
                                                        false
                                                        (throw)))))
  (get-blob [store name] (try
                           (let [s3-object (.getObject s3-client bucket-name (str path name))
                                 meta-data (.getObjectMetadata s3-object)
                                 content-length (.getContentLength meta-data)
                                 buf (byte-array content-length)]
                             (with-open [input-stream (.getObjectContent s3-object)]
                               (loop [bytes-read 0]
                                 (let [count (.read input-stream buf bytes-read (min (* 16 1024) (- content-length bytes-read)))]
                                   (if (= count -1)
                                     (assert (= bytes-read content-length)) ; TODO: don't use assert
                                     (recur (+ bytes-read count)))))
                               (Bytes/wrapArray buf)))
                           (catch AmazonS3Exception e (if (= 404 (.getStatusCode e))
                                                        nil
                                                        (throw)))))
  (delete-blob [store name] (.deleteObject s3-client bucket-name (str path name)))
  (list-blobs [store] (let [strip-key (fn [key]
                                        (assert (.startsWith key path))
                                        (.substring key (.length path)))]
                        (loop [object-listing (.listObjects s3-client (ListObjectsRequest. bucket-name path "" "" 1000))
                               so-far #{}]
                          (let [new-so-far (into so-far (map #(strip-key (.getKey %1)) (seq (.getObjectSummaries object-listing))))]
                            (if (.isTruncated object-listing)
                              (recur
                                (.listObjects s3-client (ListObjectsRequest. bucket-name path (.getMarker object-listing) "" 1000))
                                new-so-far)
                              new-so-far))))))
