  $(document).ready(function() {
    $("#addbutton").attr('disabled', 'disabled');
    $("#tag_error").hide()
    $("form").keyup(function() {
      $("#submit").attr('disabled', 'disabled');
      $("#tagid").css("color", "black");
      $("#tag_error").hide();
      // Validating Fields
      var url = $("#urlid").val();
      var extensions = url.trim().toLowerCase().split(".");

      if(extensions[extensions.length - 1] == "gif" ||extensions[extensions.length - 1] == "jpg"||extensions[extensions.length - 1] == "png"||extensions[extensions.length - 1] == "jpeg") {
        $("#url_error").hide();
      } else {
        $("#url_error").show()
      }
      var desc = $("#descid").val();
      if (!(url == "" || desc == "")) {
        $("#addbutton").removeAttr('disabled');
      }
      // Validating Tags
      var tags_string = $("#tagid").val();
      var tags_array = tags_string.split(",")
      var i;
      for (i = 0; i < tags_array.length; i++) {
        tags_array[i] = tags_array[i].trim().toLowerCase();
        if (tags_array[i].length > 20) {
          $("#addbutton").attr('disabled', 'disabled');
          $("#tagid").css("color", "red");
          $("#tag_error").show();
        }
      }
      var tags_set = new Set(tags_array);
      tags_array = [tags_set];
    })
  });
