(ns org.scode.shastity.blobstore.test
  (:require [org.scode.shastity.blobstore :as blobstore]
            [org.scode.shastity.blobstore.memory])
  (:import [org.scode.shastity.java Bytes])
  (:use [clojure.test]))

; The store name is used as a suffix on the name of each generated test.
(def testable-stores [["memory" #(org.scode.shastity.blobstore.memory.MemoryStore. (ref {}))]])

(defmacro defstore-test [base-name store-var & body]
  "Generate deftest forms for each available store to be tested; the
  body will be executed with store-var bound to a store."
  `(do
    ~@(for [[store-name store-factory] testable-stores]
      `(deftest ~(symbol (str base-name "-" store-name))
        (let [~store-var (~store-factory)]
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

(defstore-test list-blobs-empty store
  (is (= (set (seq (blobstore/list-blobs store))) #{})))

(defstore-test list-blobs-single store
  (blobstore/put-blob store "key" (Bytes/encode "value"))
  (is (= (set (seq (blobstore/list-blobs store))) #{"key"})))

(defstore-test list-blobs-multiple store
  (blobstore/put-blob store "key1" (Bytes/encode "value1"))
  (blobstore/put-blob store "key2" (Bytes/encode "value2"))
  (is (= (set (seq (blobstore/list-blobs store))) #{"key1" "key2"})))



