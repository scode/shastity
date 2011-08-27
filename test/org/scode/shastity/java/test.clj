(ns org.scode.shastity.java.test
  (:import [org.scode.shastity.java Bytes])
  (:use [clojure.test]))

(deftest byte-empty-equals
  (is (= Bytes/EMPTY (Bytes.)))
  (is (= Bytes/EMPTY Bytes/EMPTY))
  (is (= (Bytes.) (Bytes.)))
  (is (= (Bytes.) (Bytes. (byte-array 0)))))
