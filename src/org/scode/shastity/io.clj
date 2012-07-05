(ns org.scode.shastity.io
  (:import [java.io FileOutputStream]))

(defn barf-string [p contents]
  (with-open [f (FileOutputStream. (.toFile p))]
    (.write f (.getBytes contents))))
