jQuery(document).ready(function($) {
    $(".delete").click(function() {
        var clicked_element = $(this);
        $.ajax({type: "POST",
                url: $(this).attr('href'),
                success: function(data) {
                    if ($(".delete").length === 1) {
                        $("#unused_header, #unused_content")
                            .slideUp("slow", function(){
                                $("#unused_header, #unused_content").remove();
                            });
                    }
                    else {
                        clicked_element.parent().slideUp("slow", function(){
                            clicked_element.parent().remove();
                        });
                    }
                }
        });
        return false; // Prevent link launch
    });

});
