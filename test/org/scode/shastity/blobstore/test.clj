(ns org.scode.shastity.blobstore.test
  (:require [org.scode.shastity.blobstore :as blobstore]
            [org.scode.shastity.blobstore.memory])
  (:use [clojure.test]))

; The store name is used as a suffix on each generated test. Class is just the class
; to instantiate.
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




