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
  ;; c3b6 is utf-8 for o-with-two-dots, f6 is same in latin1
  (is (= 1 (.length (.decode (Bytes/fromHex "c3b6")))))
  (is (= "f6" (.toHex (Bytes. (.getBytes (.decode (Bytes/fromHex "c3b6")) "latin1"))))))

(deftest byte-hex
  (is (= "74657374" (.toHex (Bytes/encode "test"))))
  (is (= 1 (.length (Bytes/fromHex "76"))))
  (is (= "test" (.decode (Bytes/fromHex "74657374"))))
  (is (= "test" (.decode (Bytes/fromHex (.toHex (Bytes/encode "test"))))))
  (is (= "c3b6" (.toHex (Bytes/fromHex "c3b6")))))

(deftest byte-hex-full-range
  (doall (for [x (range -128 127)]
           (let [b (byte-array 1)]
             (aset-byte b 0 x)
             (is (= x (aget (.getMutableByteArray (Bytes/fromHex (.toHex (Bytes/wrapArray b)))) 0)))))))

(deftest byte-length
  (is (= 4 (.length (Bytes/encode "test")))))
