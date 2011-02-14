(ns org.scode.shastity.blobstore.test
  (:require [clojure.pprint]
            [org.scode.shastity.blobstore :as blobstore]
            [org.scode.shastity.blobstore.memory])
  (:use [clojure.test]))

; The store name is used as a suffix on each generated test. Class is just the class
; to instantiate.
(def testable-stores [["memory" org.scode.shastity.blobstore.memory.MemoryStore]])

(defmacro defstore-test [base-name store-var & body]
  "Generate deftest forms for each available store to be tested; the
  body will be executed with store-var bound to a store."
  `(do
    ~@(for [[store-name store-class] testable-stores]
      `(deftest ~(symbol (str base-name "-" store-name))
        (let [~store-var (new ~store-class)]
          ~@body)))))


(defstore-test get-from-empty store
  (is (= (blobstore/get-blob store "key") nil)))




