/// <reference types="jquery" />


function test(ai_message)
{
    console.log(ai_message);
}

function update_chat_container(ai_message)
{

    console.log("bắt đầu cập nhập");
    const container=$("#chat-container");
    const newDiv=$("<div></div>");
   
    const html= marked.parse(ai_message)
    
    newDiv.html(html);

    console.log(newDiv.html());

    newDiv.addClass("ai-bubble")

    container.append(newDiv);

    MathJax.typesetPromise([newDiv[0]]) // newDiv.get(0) để lấy phần tử DOM gốc từ đối tượng jQuery
    .then(function() {
        console.log('MathJax đã hoàn tất render các công thức toán học trong phần tử mới.');
    })
    .catch(function(err) {
        console.error('MathJax gặp lỗi khi render:', err);
    });

    container.scrollTop = container.scrollHeight;
}  

function updatePinnedStep(htmlContent) {
    const container = $("#pinned-step-container");
    container.html(htmlContent);
}

$(function() {



        console.log("jQuery đã hoạt động nội bộ");

        $("#chat-view-button").on("click",function(){
            
            update_chat_container("hello");
        });
    

    });


