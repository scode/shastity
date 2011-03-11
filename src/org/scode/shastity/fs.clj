(ns org.scode.shastity.fs
  (:require [clojure.java.io :as io]))

(defn tempfile
  ([] (tempfile "shastity-"))
  ([prefix] (tempfile prefix nil nil))
  ([prefix suffix] (tempfile prefix suffix nil))
  ([prefix suffix directory]
     (.getAbsolutePath (java.io.File/createTempFile prefix suffix (if (nil? directory) nil (io/as-file directory))))))

(defn tempdir
  ([] (tempdir "shastity-"))
  ([prefix] (tempdir prefix nil))
  ([prefix suffix] (tempdir prefix suffix nil))
  ([prefix suffix directory]
     (let [tmppath (tempfile prefix suffix directory)
           tmppath-file (java.io.File. tmppath)]
       (when-not (.delete tmppath-file)
         (throw (java.io.IOException. (str "could not delete tempfile "
                                           tmppath
                                           " for directory creation"))))
       (when-not (.mkdir tmppath-file)
         (throw (java.io.IOException. (str "could not create tempdir " tmppath))))
       tmppath)))

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



