(defproject shastity "0.1-SNAPSHOT"
  :description "De-duplicating encrypting remote backup tool"
  :url "https://github.com/scode/shastity"
  :dependencies [[org.clojure/clojure "1.2.0"]
                 [org.clojure/clojure-contrib "1.2.0"]
                 [com.amazonaws/aws-java-sdk "1.2.7"]]
  :java-source-path "java-src"
  :main org.scode.shastity.main)
