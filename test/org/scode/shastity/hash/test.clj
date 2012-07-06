(ns org.scode.shastity.hash.test
  (:require [org.scode.shastity.hash :as hash])
  (:use [clojure.test]))

(deftest hex-0-127
  (is (= "50" (hash/hex-byte (byte 80)))))

(deftest hex-128-256
  (is (= "ff" (hash/hex-byte (byte -1)))))

(deftest sha256
  (is (= "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
         (hash/sha256-hex (.getBytes "test")))))
