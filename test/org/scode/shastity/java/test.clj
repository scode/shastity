(ns org.scode.shastity.java.test
  (:import [org.scode.shastity.java Bytes])
  (:use [clojure.test]))

(deftest byte-empty-equals
  (is (= Bytes/EMPTY (Bytes.))))
