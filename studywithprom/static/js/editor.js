// this a best method of saving the form 
// this almost done but incomplete
// it stores all the data of the page at a time
// and then send it to the server using ajax and json

  $('#saveform').click(function(){
    var  form_title = $('#form_title').val();
    var  form_desc = $('#form_desc').val();
    var  form_exdate = $('#form_exdate').val(); 
    var  form_loginreq = $('#form_loginreq').is(':checked');
    // var unsaved = $('[data-catid=-1]');
    var unsaved = $('.oneq:not(#headQ)');

    jsonlist={};
    unsaved.each(function(i, obj) {
      var qid = $(obj).attr("data-catid");
      var title = $(obj).find('.question').val();
      var ind = $(obj).find('.qtype_select')[0].selectedIndex;
      var isreq = $(obj).find(".isreq").is( ":checked" );
      var isother = false;
      var optdic ={};
      var constraint = {};
      if(ind >=2 && ind <=4){
        isother = $(obj).find(".isother").is( ":checked" );
        var alloptns = $(obj).find(".optans  ol  input");
        alloptns.each(function(j, obj) {
            var optid = $(obj).attr("data-catid");
            var thisoptdict = {"optid":optid, "optvalue": $(obj).val() }
           optdic[j] = thisoptdict;
         });
      }
      else if(ind ==5){ 
        var allcontrnt = $(obj).find(".linearans input");
        allcontrnt.each(function(k, obj) {
           constraint[k] = $(obj).val();
         });

      }
      else{}



      mydict = {"qid":qid, "title":title, "type":ind, "isreq":isreq, 
                "isother":isother, "optdic":optdic, "constraint":constraint};

      jsonlist[i]=mydict;
    });

  $.ajax(
  {
      type:"post",
      url: "/user/{{user.id}}/saveform/{{form.survey.id}}",
      data:{
               form_title: form_title ,
               form_desc: form_desc ,
               form_exdate: form_exdate ,
               form_loginreq: form_loginreq,
               jsonlist: JSON.stringify(jsonlist)
      },
      headers: {'X-CSRFToken': '{{ csrf_token }}'},
      success: function( data ) 
      {
      }
   })
});
