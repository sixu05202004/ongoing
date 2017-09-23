package com.test.Controller;

import com.test.domain.ConfigBean;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Created by dengdan on 2017/9/12.
 */
@RestController
public class UserController {
    @Autowired
    ConfigBean configBean;

    @RequestMapping("/")
    public String hexo(){
        return configBean.getName()+configBean.getResult();
    }
}
