(ns org.scode.shastity.fs.test
  (:require [clojure.java.io :as io]
            [org.scode.shastity.fs :as fs])
  (:use [clojure.test]))

(deftest tempfile
  (let [tmpfile (fs/tempfile)]
    (is (fs/exists tmpfile))
    (fs/delete tmpfile)))

(deftest tempfile-prefix
  (let [tmpfile (fs/tempfile "prefix")]
    (is (fs/exists tmpfile))
    (is (.startsWith (fs/as-string (.getFileName tmpfile)) "prefix"))
    (fs/delete tmpfile)))

(deftest tempfile-suffix-directory
  (let [tmpfile (fs/tempfile "prefix" "suffix")]
    (is (fs/exists tmpfile))
    (is (.startsWith (fs/as-string (.getFileName tmpfile)) "prefix"))
    (is (.endsWith (fs/as-string (.getFileName tmpfile)) "suffix"))
    (fs/delete tmpfile)))

(deftest tempdir
  (let [tmpdir (fs/tempdir)]
    (is (fs/exists tmpdir))
    (fs/delete tmpdir)))

(deftest tempdir-prefix
  (let [tmpdir (fs/tempfile "prefix")]
    (is (fs/exists tmpdir))
    (is (.startsWith (fs/as-string (.getFileName tmpdir)) "prefix"))
    (fs/delete tmpdir)))

(deftest tempdir-suffix-directory
  (let [tmpdir (fs/tempfile "prefix" "suffix")]
    (is (fs/exists tmpdir))
    (is (.startsWith (fs/as-string (.getFileName tmpdir)) "prefix"))
    (is (.endsWith (fs/as-string (.getFileName tmpdir)) "suffix"))
    (fs/delete tmpdir)))

; TODO: Test w/ directory once we have tempdir.

(deftest with-tempfile
  (with-local-vars [path-var nil]
    (fs/with-tempfile [tmpfile]
      (is (fs/exists tmpfile))
      (var-set path-var tmpfile))
    (is (not (fs/exists (var-get path-var))))))

(deftest with-tempfile-args-passed
  (with-local-vars [path-var nil]
    (fs/with-tempfile [tmpfile "prefix" "suffix"]
      (is (fs/exists tmpfile))
      (is (.startsWith (fs/as-string (.getFileName tmpfile)) "prefix"))
      (is (.endsWith (fs/as-string (.getFileName tmpfile)) "suffix"))
      (var-set path-var tmpfile))
    (is (not (fs/exists (var-get path-var))))))

