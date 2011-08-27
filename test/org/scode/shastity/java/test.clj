(ns org.scode.shastity.java.test
  (:import [org.scode.shastity.java Bytes])
  (:use [clojure.test]))

(deftest byte-empty-equals
  (is (= Bytes/EMPTY (Bytes.)))
  (is (= Bytes/EMPTY Bytes/EMPTY))
  (is (= (Bytes.) (Bytes.)))
  (is (= (Bytes.) (Bytes. (byte-array 0)))))

(deftest byte-empty-utf8
  (is (= "" (.toStringFromUtf8 Bytes/EMPTY)))
  (is (= "" (.toStringFromUtf8 (Bytes/fromString "")))))

(deftest byte-wrap
  (let [b (byte-array 1)]
    (is (= b (.getMutableByteArray (Bytes/wrapArray b))))))

(deftest byte-utf8
  (is (= "åäö" (.toStringFromUtf8 (Bytes/fromString "åäö")))))

(deftest byte-hex
  (is (= "74657374" (.toHex (Bytes/fromString "test"))))
  (is (= 1 (.length (Bytes/fromHex "76"))))
  (is (= "test" (.toStringFromUtf8 (Bytes/fromHex "74657374"))))
  (is (= "test" (.toStringFromUtf8 (Bytes/fromHex (.toHex (Bytes/fromString "test")))))))
