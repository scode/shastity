(defproject shastity "0.1-SNAPSHOT"
  :description "De-duplicating encrypting remote backup tool"
  :url "https://github.com/scode/shastity"
  :dependencies [[org.clojure/clojure "1.4.0"]
                 [com.amazonaws/aws-java-sdk "1.2.10"]
                 [org.clojure/tools.cli "0.2.1"]]
  :java-source-path "java-src"
  :main org.scode.shastity.main)
