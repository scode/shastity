(ns org.scode.shastity.manifest.test
  (:require [org.scode.shastity.manifest :as manifest])
  (:import [org.scode.shastity.java Bytes])
  (:use [clojure.test]))

(defmacro with-store [[name] & body]
  "Execute body with a memory store bound to the given name."
  `(let [~name (org.scode.shastity.blobstore.memory.MemoryStore. (ref {}))]
     ~@body))

(deftest string-encode
  (is (= "test" (manifest/encode "test")))
  (is (= "%24test" (manifest/encode "$test")))
  (is (= "%25test" (manifest/encode "%test")))
  (is (= "%c3%b6" (manifest/encode (.decode (Bytes/fromHex "c3b6"))))))

(deftest string-decode
  (is (= "test" (manifest/decode "test")))
  (is (= "$test" (manifest/decode "%24test")))
  (is (= "%test" (manifest/decode "%25test")))
  (is (= (.decode (Bytes/fromHex "c3b6")) (manifest/decode "%c3%b6"))))

(deftest decode-object
  (let [meta (manifest/encode "{:key 1}")]
    (is (= ["name" {:key 1} ["hash1"]] (manifest/decode-object (str "name " meta " hash1"))))
    (is (= ["name" {:key 1} []] (manifest/decode-object (str "name " meta))))
    (is (= ["name" {:key 1} ["hash1" "hash2"]] (manifest/decode-object (str "name " meta " hash1 hash2"))))))

(deftest encode-object
  (doseq [[name meta hashes] [["name" {:key 1} []]
                            ["name" {:key 1} [ "deadbeef" ]]
                            ["name" {:key 1} [ "daedbeef" "beefdead" ]]]]
    (is (= [name meta hashes] (manifest/decode-object (manifest/encode-object [name meta hashes]))))))

(deftest empty-manifest
  (with-store [store]
    (let [writer (manifest/create-manifest-writer)]
      (manifest/freeze writer)
      (manifest/upload writer store "empty-manifest"))
    (let [reader (manifest/create-manifest-reader)]
      (is (= (seq []) (manifest/get-objects reader store "empty-manifest"))))))



