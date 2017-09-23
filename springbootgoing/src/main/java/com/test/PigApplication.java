package com.test;

import com.test.domain.ConfigBean;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.SpringBootConfiguration;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;


@SpringBootApplication
@EnableConfigurationProperties({ConfigBean.class})
public class PigApplication {

	public static void main(String[] args) {
		SpringApplication.run(PigApplication.class, args);
	}
}
