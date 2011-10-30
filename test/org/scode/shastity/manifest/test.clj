(ns org.scode.shastity.manifest.test
  (:require [org.scode.shastity.manifest :as manifest])
  (:import [org.scode.shastity.java Bytes])
  (:use [clojure.test]))

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

(deftest parse-object
  (is (= ["name" "meta" ["hash1"]] (manifest/parse-object "name meta hash1")))
  (is (= ["name" "meta" []] (manifest/parse-object "name meta")))
  (is (= ["name" "meta" ["hash1" "hash2"]] (manifest/parse-object "name meta hash1 hash2"))))




