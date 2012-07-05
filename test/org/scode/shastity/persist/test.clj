(ns org.scode.shastity.persist.test
  (:require [org.scode.shastity.persist :as persist]
            [org.scode.shastity.fs :as fs]
            [org.scode.shastity.io :as io]
            [org.scode.shastity.blobstore.memory :as memory])
  (:use [clojure.test]))

(defn create-hier [base entries]
  (doseq [[type rest] entries]
    (cond
      (= :dir type) (let [[name dir-entries] rest]
                      (fs/mkdir (fs/resolve base name))
                      (create-hier (fs/resolve base name) dir-entries))
      (= :file type) (let [[name contents] rest]
                       (io/barf-string (fs/resolve base name) contents))
      :else (throw (AssertionError. "invalid type")))))

(defn memory-store []
  (org.scode.shastity.blobstore.memory.MemoryStore. (ref {})))

; Use small block size for more comfortable testing using small pieces of data.
(def ^:dynamic *block-size* 5)

; TODO: don't pollute with tempdir
(deftest mixed-persist
  (let [temp-dir (fs/tempdir)]
    (create-hier temp-dir [[:file ["testfile" "testcontents"]]
                           [:dir ["subdir" [[:file ["subdirfile" "cont"]]]]]])
    (persist/persist-dir temp-dir (memory-store) *block-size*)))

