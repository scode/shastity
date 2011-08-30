(ns org.scode.shastity.blobstore.test
  (:require [org.scode.shastity.blobstore :as blobstore]
            [org.scode.shastity.blobstore.memory]
            [org.scode.shastity.blobstore.s3])
  (:import [org.scode.shastity.java Bytes]
           [com.amazonaws.services.s3 AmazonS3Client]
           [com.amazonaws.auth BasicAWSCredentials])
  (:use [clojure.test]))

; The store name is used as a suffix on the name of each generated test.
(def testable-stores (apply hash-map (flatten (filter #(not (nil? %1))
                       [["memory" #(org.scode.shastity.blobstore.memory.MemoryStore. (ref {}))]
                        (if (System/getenv "SHASTITY_UNITTEST_S3_BUCKET_NAME")
                          ["s3" (fn [] (let [access-key (System/getenv "SHASTITY_UNITTEST_S3_ACCESS_KEY")
                                              secret-key (System/getenv "SHASTITY_UNITTEST_S3_SECRET_KEY")
                                              bucket-name (System/getenv "SHASTITY_UNITTEST_S3_BUCKET_NAME")
                                              bucket-path (System/getenv "SHASTITY_UNITTEST_S3_BUCKET_PATH")
                                              s3-client (AmazonS3Client. (BasicAWSCredentials. access-key secret-key))]
                                         ;; Use time + random to "ensure" we get a clean slate. Yes, we're leaving stuff
                                         ;; after unit testing for now.
                                         (org.scode.shastity.blobstore.s3.S3Store.
                                           s3-client
                                           bucket-name
                                           (str bucket-path "/" (System/currentTimeMillis) "/" (Math/random)))))]
                          nil)]))))

(defmacro defstore-test [base-name store-var & body]
  "Generate deftest forms for each available store to be tested; the
  body will be executed with store-var bound to a store."
  `(do
    ~@(for [[store-name store-factory] testable-stores]
      `(deftest ~(symbol (str base-name "-" store-name))
        (let [~store-var ((get testable-stores ~store-name))]
          ~@body)))))

(defstore-test get-from-empty store
  (is (= (blobstore/get-blob store "key") nil)))

(defstore-test put-into-empty store
  (blobstore/put-blob store "key" (Bytes/encode "value"))
  (is (= (blobstore/get-blob store "key") (Bytes/encode "value"))))

(defstore-test put-empty-blob store
  (blobstore/put-blob store "key" (Bytes/encode ""))
  (is (= (blobstore/get-blob store "key") (Bytes/encode ""))))

(defstore-test existence-check store
  (is (not (blobstore/has-blob store "key")))
  (blobstore/put-blob store "key" (Bytes/encode ""))
  (is (blobstore/has-blob store "key")))

(defstore-test delete store
  (blobstore/put-blob store "key" (Bytes/encode "value"))
  (is (= (blobstore/get-blob store "key") (Bytes/encode "value")))
  (blobstore/delete-blob store "key")
  (is (= (blobstore/get-blob store "key") nil)))

(defstore-test delete-non-existing store
  (is (not (blobstore/has-blob store "key")))
  (blobstore/delete-blob store "key"))

(defstore-test list-blobs-empty store
  (is (= (set (seq (blobstore/list-blobs store))) #{})))

(defstore-test list-blobs-single store
  (blobstore/put-blob store "key" (Bytes/encode "value"))
  (is (= (set (seq (blobstore/list-blobs store))) #{"key"})))

(defstore-test list-blobs-multiple store
  (blobstore/put-blob store "key1" (Bytes/encode "value1"))
  (blobstore/put-blob store "key2" (Bytes/encode "value2"))
  (is (= (set (seq (blobstore/list-blobs store))) #{"key1" "key2"})))

(defstore-test list-blobs-many store
  ; This is currently pretty s3 specific in its usefulness. Set page size small enough
  ; that we can comfortable do our "more than a page or two" unit test with a reasonable
  ; number of accesses. Should maybe not use defstore-test for this and just specifically
  ; test s3.
  (binding [org.scode.shastity.blobstore.s3/*s3-listing-page-size* 3]
    (doall (for [i (range 10)]
             (blobstore/put-blob store (str "key" i) (Bytes/encode (str "value" i)))))
    (is (= (set (seq (blobstore/list-blobs store))) (set (map #(str "key" %1) (range 10)))))))



