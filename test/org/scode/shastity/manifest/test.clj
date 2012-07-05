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

;(deftest decode-object
;  (let [meta (manifest/encode "{:key 1}")]
;    (is (= ["name" {:key 1} ["hash1"]] (manifest/decode-object (str "name " meta " hash1"))))
;    (is (= ["name" {:key 1} []] (manifest/decode-object (str "name " meta))))
;    (is (= ["name" {:key 1} ["hash1" "hash2"]] (manifest/decode-object (str "name " meta " hash1 hash2"))))))

;(deftest encode-object
;  (doseq [[name meta hashes] [["name" {:key 1} []]
;                            ["name" {:key 1} [ "deadbeef" ]]
;                            ["name" {:key 1} [ "daedbeef" "beefdead" ]]]]
;    (is (= [name meta hashes] (manifest/decode-object (manifest/encode-object [name meta hashes]))))))

;(defmacro defmanifest-identity [name manifest-entries]
;  "Define a test with the given name suffix and the given manifest entries, which will
;  create a temporary store and write a manifest to it containing the given files (in the order
;  given). Then, read manifest back and compare to make sure the returned sequence of entries
;  is identical to the *sorted* original sequence."
;  `(deftest ~(symbol (str "manifest-identity-" name))
;     (with-store [store#]
;       (let [entries# ~manifest-entries]
;         (let [writer# (manifest/create-manifest-writer)]
;           (doseq [[path# meta# hashes#] entries#]
;             (manifest/add-object writer# path# meta# hashes#))
;           (manifest/freeze writer#)
;           (manifest/upload writer# store# "manifest"))
;         (let [reader# (manifest/create-manifest-reader)]
;           (is (= (seq (sort manifest/manifest-entry-comparator entries#))
;                  (seq (manifest/get-objects reader# store# "manifest")))))))))

;(defmanifest-identity empty [])
;(defmanifest-identity one-entry [["name" {:key "value"} ["deadbeef"]]])
;(defmanifest-identity one-entry-nohashes [["name" {:key "value"} []]])
;(defmanifest-identity one-entry-multiple-hashes [["name" {:key "value"} ["deadbeef" "beefdead"]]])
;(defmanifest-identity multiple-entries [["a" {:key 1} ["dead"]]
;                                        ["b" {:key 2} ["beef"]]
;                                        ["c" {:key 3} ["00ba"]]])
;(defmanifest-identity multiple-entries-unordered [["b" {:key 2} ["beef"]]
;                                                  ["a" {:key 1} ["dead"]]
;                                                  ["c" {:key 3} ["00ba"]]])



