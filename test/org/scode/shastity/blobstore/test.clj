(ns org.scode.shastity.blobstore.test
  (:require [org.scode.shastity.blobstore :as blobstore]
            [org.scode.shastity.blobstore.memory])
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

(defn beq [a b]
  "Corerce both to byte array and compare"
  (let [a-ba (if (string? a) (.getBytes a) a)
        b-ba (if (string? b) (.getBytes b) b)]
        (java.util.Arrays/equals a-ba b-ba)))

(defstore-test get-from-empty store
  (is (= (blobstore/get-blob store "key") nil)))

(defstore-test put-into-empty store
  (blobstore/put-blob store "key" (.getBytes "value"))
  (is (beq (blobstore/get-blob store "key") "value")))

(defstore-test put-empty-blob store
  (blobstore/put-blob store "key" (.getBytes ""))
  (is (beq (blobstore/get-blob store "key") (.getBytes ""))))

(defstore-test existence-check store
  (is (not (blobstore/has-blob store "key")))
  (blobstore/put-blob store "key" (.getBytes ""))
  (is (blobstore/has-blob store "key")))

(defstore-test delete store
  (blobstore/put-blob store "key" (.getBytes "value"))
  (is (beq (blobstore/get-blob store "key") "value"))
  (blobstore/delete-blob store "key")
  (is (beq (blobstore/get-blob store "key") nil)))

(defstore-test list-blobs-empty store
  (is (= (set (seq (blobstore/list-blobs store))) #{})))

(defstore-test list-blobs-single store
  (blobstore/put-blob store "key" (.getBytes "value"))
  (is (= (set (seq (blobstore/list-blobs store))) #{"key"})))

(defstore-test list-blobs-multiple store
  (blobstore/put-blob store "key1" (.getBytes "value1"))
  (blobstore/put-blob store "key2" (.getBytes "value2"))
  (is (= (set (seq (blobstore/list-blobs store))) #{"key1" "key2"})))



