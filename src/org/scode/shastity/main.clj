(ns org.scode.shastity.main
  (:gen-class)
  (:require [clojure.contrib.command-line :as cmdline]))

(defn -main [& args]
  (cmdline/with-command-line args
    "shastity - remote de-duplicated encrypted backups"
    []
    (println "not yet implemented :(")))
