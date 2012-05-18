(ns org.scode.shastity.main
  (:gen-class)
  (:require [clojure.tools.cli :as cli]))

(defn -main [& args]
  (cli/cli args)
    (println "not yet implemented :("))
