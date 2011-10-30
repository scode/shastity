(ns org.scode.shastity.blobstore.s3
  (:require [org.scode.shastity.blobstore :as blobstore])
  (:import [org.scode.shastity.java Bytes]
           [com.amazonaws.services.s3.model ObjectMetadata ListObjectsRequest AmazonS3Exception]))

(def ^:dynamic *s3-listing-page-size* 1000) ; def:ed so that unit tests can control it

(deftype S3Store [s3-client bucket-name path]
  ;; TODO: prefix vs. path; validate trailing / if need be
  ;; TODO: existence check triggers spurious logging by the AWS SDK :(
  blobstore/BlobStore
  (put-blob [store name value] (let [meta-data (ObjectMetadata.)]
                                 (.setContentLength meta-data (.length value))
                                 (.putObject s3-client bucket-name (str path name) (.getInputStream value) meta-data)))
  ; Would be really nice of S3 has an if-not-exists feature here.
  (put-blob-if-absent [store name value] (if (not (blobstore/has-blob store name)) (blobstore/put-blob store name value)))
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
                                        (.substring key (.length path)))
                            get-listing (fn get-listing ([] (get-listing ""))
                                                        ([marker] (.listObjects s3-client (ListObjectsRequest. bucket-name path marker "" (Integer. *s3-listing-page-size*)))))
                            summaries-to-keys (fn [summaries] (map #(strip-key (.getKey %1)) summaries))
                            lazy-iter (fn lazy-iter ([object-listing] (lazy-iter object-listing (summaries-to-keys (seq (.getObjectSummaries object-listing)))))
                                                    ([object-listing cur-keys]
                                                      (if (seq cur-keys)
                                                        (cons (first cur-keys) (lazy-seq (lazy-iter object-listing (rest cur-keys))))
                                                        (if (.isTruncated object-listing)
                                                          (let [next-listing (get-listing (.getNextMarker object-listing))
                                                                object-summaries (summaries-to-keys (seq (.getObjectSummaries next-listing)))]
                                                            (if (not object-summaries)
                                                              nil ; prevent infinite recursion in case of buggy s3 backend
                                                              (cons (first object-summaries) (lazy-seq (lazy-iter next-listing (rest object-summaries))))))
                                                          nil))))]
                         (lazy-seq (lazy-iter (get-listing))))))
