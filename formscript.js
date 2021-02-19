
function onSubmit(e) {
    var form = FormApp.getActiveForm();
    var allResponses = form.getResponses();
    var latestResponse = allResponses[allResponses.length - 1];
    var response = latestResponse.getItemResponses();
    var data ={};

    for (var i = 0; i < response.length; i++) 
    {
        var question = response[i].getItem().getTitle();
        var answer = response[i].getResponse();
        
        Logger.log(question + ' ' + answer);

        try {
            var parts = answer.match(/[\s\S]{1,1024}/g) || [];
        } catch (e) {
            var parts = answer;
        }

        if (answer == "") {
            continue;
        }

        var new_ans = [];

        for (var j = 0; j < parts.length; j++) {
            new_ans.push(parts[j]);
        }

        data[question] =  new_ans;
    }

    var start_time = data["Start Date"] + "T" + data["Start Time"] + ":00+05:30";
    var end_time = data["Start Date"] + "T" + data["End Time"] + ":00+05:30";

    var end_date = data["End Date"];// + "T" + data["End Time"] + ":00+04:00";
    // Logger.log(start_date+" "+ data["Weekdays"])

    // for(var en in CalendarApp.Weekday)
    //   Logger.log("en_num: "+en);

    for(var i=0;i<data["Weekdays"].length;++i)
    {
      var day = data["Weekdays"][i].toUpperCase();
      Logger.log(day);
      Logger.log(CalendarApp.Weekday[day])
      var eventSeries = CalendarApp.getDefaultCalendar().createEventSeries('trial',new Date(start_time),new Date(end_time),
                        CalendarApp.newRecurrence().addWeeklyRule()
                                   .onlyOnWeekday(CalendarApp.Weekday[day])
                                   .until(new Date(end_date)));
    }
    Logger.log(data);
};