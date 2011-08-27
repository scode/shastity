(ns org.scode.shastity.java.test
  (:import [org.scode.shastity.java Bytes])
  (:use [clojure.test]))

(deftest byte-empty-equals
  (is (= Bytes/EMPTY (Bytes.)))
  (is (= Bytes/EMPTY Bytes/EMPTY))
  (is (= (Bytes.) (Bytes.)))
  (is (= (Bytes.) (Bytes. (byte-array 0)))))

(deftest byte-empty-utf8
  (is (= "" (.decode Bytes/EMPTY)))
  (is (= "" (.decode (Bytes/encode "")))))

(deftest byte-wrap
  (let [b (byte-array 1)]
    (is (= b (.getMutableByteArray (Bytes/wrapArray b))))))

(deftest byte-utf8
  (is (= "åäö" (.decode (Bytes/encode "åäö")))))

(deftest byte-hex
  (is (= "74657374" (.toHex (Bytes/encode "test"))))
  (is (= 1 (.length (Bytes/fromHex "76"))))
  (is (= "test" (.decode (Bytes/fromHex "74657374"))))
  (is (= "test" (.decode (Bytes/fromHex (.toHex (Bytes/encode "test")))))))
