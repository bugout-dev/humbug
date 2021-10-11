# Java humbug library

Contents
1. [Install](#install)
2. [Reporting in java](#java)
3. [Reporting in clojure](#clojure)
## How to use:
### Install
#### Add library to your maven project's `pom.xml` under `<dependencies>` parameter:
```xml
<dependency>
    <groupId>dev.bugout.humbug</groupId>
    <artifactId>humbug</artifactId>
    <version>0.0.3</version>
</dependency>
```
#### Add github repository to your `pom.xml` under `<repositories>` parameter, so maven can understand that it needs to download library from github packages
```xml
<repository>
    <id>github</id>
    <name>GitHub Bugout Apache Maven Packages</name>
    <url>https://maven.pkg.github.com/bugout-dev/humbug</url>
    <releases><enabled>true</enabled></releases>
    <snapshots><enabled>true</enabled></snapshots>
</repository>
```
#### If you haven't added github server to maven settings in `~/.m2/settings.xml`, add it under `<servers>` parameter:
```xml
<server>
  <id>github</id>
  <username>GITHUB_USERNAME</username>
  <password>TOKEN</password>
</server>
```
* **GITHUB_USERNAME** : Your username
* **TOKEN** : Personal token of github, with permission to read packages
#### If you don't have `~/.m2/settings.xml` file, create it and pase following code:
```xml
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0
                      http://maven.apache.org/xsd/settings-1.0.0.xsd">
  <servers>
    <server>
      <id>github</id>
      <username>GITHUB_USERNAME</username>
      <password>TOKEN</password>
    </server>
  </servers>
</settings>

```
### Reporting
## Java
``` java
import dev.bugout.humbug.ContentBuilder;
import dev.bugout.humbug.HumbugConsent;
import dev.bugout.humbug.Reporter;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

public class Example {
    public static void main(String[] args) {
    
        HumbugConsent consent = new HumbugConsent();    
        String token = "<ADD_YOUR_TOKEN_HERE>";   //Your bugout token
        Reporter r = new Reporter(
                "java app",            //Name of reports
                 consent,               //Consent 
                 "<client_id>",         //Client Id
                 "<session_id>",        //Session Id
                 token                  //bugout-dev Integration token
        );

        r.systemReport("0.0.2", "test");  //Reporting system information

        // Exception report examples:
        try {
            int i = 1/0;
        }
        catch (Exception e) {
            r.errorReport(e, "0.0.2", "test");
        }

        try {
            InputStream i = new FileInputStream("not_existed_file");
        }
        catch (IOException e) {
            r.errorReport(e, "0.0.2", "test");
        }

        //Custom report example
        String content = new ContentBuilder()
                .addHeader("Custom header")
                .addMultilineCode("Testing java")
                .toString();
        r.customReport("Custom title", content, "important", "wtf");
    }
}
```

## Clojure
```clojure
(ns humbug-demo
  (:import (dev.bugout.humbug HumbugConsent ConsentMechanism Reporter)))

(def consent (HumbugConsent. true))                         ;Consent with boolean
(println (.check consent))

(defn functional_mechanism [f]                              ;ConsentMechanism constructor
  (reify
    ConsentMechanism
    (call [this] (f))
    )
  )

(def demo-mechanism (functional_mechanism (fn [] true)))    ;ConsentMechanism examples
(def demo-mechanism2 (functional_mechanism
                       (fn []
                         (true? true)
                         ))
  )

(def consent-functional (HumbugConsent. (into-array (list demo-mechanism demo-mechanism2))))
                                                            ;Consent with functions


(println (.check consent-functional))

(def TOKEN "95cfa467-94ae-4891-951b-7874d6a13e2c")
(def reporter (Reporter. "clojure reporter" consent "300" "300" TOKEN))
(def tags  (into-array (list "clojure" "test")))

(.systemReport reporter tags)                               ;Reporting system information

(try
  (/ 1 0)
  (catch Exception e (.errorReport reporter e tags)))       ;Exception reporting

(try
  (throw (Exception. "exception"))
  (catch Exception e (.errorReport reporter e tags)))

(try
  (throw
    (ex-info "The ice cream has melted!"
             {:causes             #{:fridge-door-open :dangerously-high-temperature}
              :current-temperature {:value 25 :unit :celsius}}))
  (catch Exception e (.errorReport reporter e tags)))

(.customReport reporter "Clojure" "Hello from clojure" tags) ;Custom reporting
```
