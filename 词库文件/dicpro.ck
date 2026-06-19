你好
res = $访问 http://110.41.8.213:8000/api/emojis/list?n={'data':7789} get$
cs = '你好'
如果 cs == '你好'
$发送 %QQ%$
$发送 %群号%$
$发送 %昵称%$
如果尾
另如果 cs == 7788
$发送 %res%$
$写文件 测试 a %res%$
如果尾
否则
$发送 %晚上%$

再见
i = 0
data = $读文件 777 455 111$
循环(%i% := %i% + data) < 5
$发送 666$
循环True

访问测试
res = $访问 http://110.41.8.213:8000/api/emojis/list get$
data = @%res%#files
kd_data = {
  "rows": [
    {
      "buttons": [
        {
          "id": "btn_1781433837842",
          "render_data": {
            "label": "按钮",
            "visited_label": "以按",
            "style": 1
          },
          "action": {
            "type": 1,
            "data": "777888",
            "permission": {
              "type": 2
            },
            "reply": True,
            "enter": True
          }
        }
      ]
    }
  ]
}
$发送 %data%±md content=\n#你好±±at id=%QQ%±±kd content=%kd_data%±$
$调用 你好$

测试
a1 = 2
a2 = 8
a3 = 7788
a=$计算 [a3*[a1+a2*a3]]$

括号测试([\s\S]*)
a = %括号1%
$发送 %a%$

测试md([\s\S]*)#([\s\S]*)
a = $直发按钮 %括号1% %括号2%$
$发送 ±md content=%a%±$

网页图测试(.*)
a = $html %括号1% 1080 1080$
$发送 ±img url=%a%±$


调用测试
$调用 你好$
$调用 你好 #测试#参数2=长沙市$

[内部]你好
a="""**加粗**\n__下划线加粗__"""
b="""
**加粗**
__下划线加粗__
_斜体_
*星号斜体*
***加粗斜体***
~~删除线~~
"""
$发送 ±md content=#调用测试%a%±$
$发送 ±md content=#区别%b%±$

[内部]你好[参数1 参数2]
a=2
返回 a, a