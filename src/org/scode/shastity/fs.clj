(ns org.scode.shastity.fs
  (:require [clojure.java.io :as io]))

(defn tempfile
  ([] (tempfile "shastity-"))
  ([prefix] (tempfile prefix nil nil))
  ([prefix suffix] (tempfile prefix suffix nil))
  ([prefix suffix directory]
    (.getAbsolutePath (java.io.File/createTempFile prefix suffix (if (nil? directory) nil (io/as-file directory))))))

(defmacro with-tempfile [[path-var & rest] & body]
  "Evaluate body with a temporary file path bound to path-var; delete temporary file after
  body evaluates.

  If the body deletes the file, an exception won't be raced but the caller will have introduced
  a potential race condition. The body should only ever delete the file if done in a context where
  race conditions are not a problem."
  `(let [~path-var (tempfile ~@rest)]
    (try
      (do
        ~@body)
      (finally (.delete (io/as-file ~path-var))))))



