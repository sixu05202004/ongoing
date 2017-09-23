package com.test.domain;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.PropertySource;

/**
 * Created by dengdan on 2017/9/12.
 */

@Configuration
@ConfigurationProperties(prefix = "com.md")
@PropertySource("classpath:test.properties")
public class ConfigBean {
    private String name;
    private String result;

    public String getName() {
        return name;
    }

    public String getResult() {
        return result;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setResult(String result) {
        this.result = result;
    }
}
