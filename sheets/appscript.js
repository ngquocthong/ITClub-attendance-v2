var sheet_id = "1Gq9yOx5RAvuCnRF77rIPt5JFYAgFcQvO5PNKiKnfsnw";
var sheet_DiemDanh = "DiemDanh";
var sheet_BangDiem = "BangDiem";
var sheet_ThongTin = "ThongTin";
var sheet_ViPham = "ViPham";

function doGet(e) {
  var ss = SpreadsheetApp.openById(sheet_id);
  var sheet = ss.getSheetByName(sheet_DiemDanh);
  var students_sheet = ss.getSheetByName(sheet_ThongTin);

  // arduino - read data
  var sheetRead = ss.getSheetByName('ViPham');
  var read = e.parameter.read;
  if (read !== undefined) {
    var numRows = sheetRead.getLastRow() - 1;
    var numCols = sheetRead.getLastColumn();
    //var dataRange = sheetRead.getRange(2, 1, numRows, numCols);
    //var data = dataRange.getValues();
    var data = sheetRead.getDataRange().getValues();
    var result = '';
    for (var i = 0; i <= numRows; i++) {
      var row = data[i];
      if (row[0] !== '') {
        var name = row[0];
        var sdt = row[1];
        var status = row[2];
        result += 'Name: ' + name + ', SDT: ' + sdt + ', Status: ' + status + ',; ';
      } else {
        break;
      }
    }
    var sheet_DD = ss.getSheetByName(sheet_DiemDanh);
    var sheet_VP = ss.getSheetByName(sheet_ViPham);
    var rangeToClear = sheet_VP.getRange(2, 1, sheet_VP.getLastRow() - 1, sheet_VP.getLastColumn());
    sheet_DD.clearContents();
    sheet_VP.clearContents();
    return ContentService.createTextOutput(result);
  } else {
    var student_id = Number(e.parameter.cardid);  // assume the ID is sent as a parameter from Arduino
    var student_name = getStudentName(students_sheet, student_id);  // retrieve the name of the student based on their ID
    var date = new Date();
    var studentIds = sheet.getRange("A:A").getValues().flat();
    if (student_id != '12515838' && !studentIds.includes(student_id)){
      sheet.appendRow([student_id, student_name, date]);  // write the student name, sensor data, and date to the "Data" sheet  
    }
      
    if (student_id == '12515838') // master
    {
      var sheet_TT = ss.getSheetByName(sheet_ThongTin);
      var sheet_DD = ss.getSheetByName(sheet_DiemDanh);
      var sheet_VP = ss.getSheetByName(sheet_ViPham);
      var thongtin_data = sheet_TT.getDataRange().getValues();
      var diemdanh_data = sheet_DD.getDataRange().getValues();
      var vipham_data = sheet_VP.getDataRange().getValues();
      var violated_ids = [];

      for (var i = 0; i < thongtin_data.length; i++) {
        var id = thongtin_data[i][0];
        //var name = thongtin_data[i][1];
        var found = false;
        for (var j = 0; j < diemdanh_data.length; j++) {
          var diemdanh_id = diemdanh_data[j][0];
          if (id == diemdanh_id) {
            found = true;
            break;
          }
        }
        if (!found) {
          //violated_ids.push(i + 1); // add row number to the list of violated IDs
          //ar row = thongtin_data[i];
          sheet_VP.appendRow([thongtin_data[i][1], "'" + thongtin_data[i][2], "vang vao ngay " + date.getDate().toString() + " thang " + date.getMonth().toString()]); // write the row to the "ViPham" sheet
        }
      }

    }
  }
}

function doPost(e) {
  var ss = SpreadsheetApp.openById(sheet_id);
  var sheet = ss.getSheetByName(sheet_BangDiem);
  var student_id = String(e.parameter.id);
  var student_subject = String(e.parameter.mon);
  var student_point = Number(e.parameter.diem);

  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (student_id == data[i][0]) {
      if (student_subject == "nguvan") { sheet.getRange(i + 1, 3).setValue(student_point); }
      if (student_subject == "tienganh") { sheet.getRange(i + 1, 4).setValue(student_point); }
      if (student_subject == "toan") { sheet.getRange(i + 1, 5).setValue(student_point); }
      if (student_subject == "lichsu") { sheet.getRange(i + 1, 6).setValue(student_point); }
      if (student_subject == "khtn") { sheet.getRange(i + 1, 7).setValue(student_point); }
      if (student_subject == "tinhoc") { sheet.getRange(i + 1, 8).setValue(student_point); }

    }
  }


  //sheet.appendRow([student_id, student_subject, student_point]);
  if (student_point < 5) {
    var sheet_TT = ss.getSheetByName(sheet_ThongTin);
    var sheet_VP = ss.getSheetByName(sheet_ViPham);


    var data = sheet_TT.getDataRange().getValues();
    for (var i = 0; i < data.length; i++) {
      if (data[i][0] == student_id) {
        sheet_VP.appendRow([data[i][1], "'" + data[i][2], "diem kem mon " + student_subject]);
        break; // Exit the loop after the row is moved to the "ViPham" sheet
      }
    }
  }
}

function getStudentName(sheet_ThongTin, cardid) {
  var data = sheet_ThongTin.getDataRange().getValues();
  for (var i = 0; i < data.length; i++) {
    if (data[i][0] == cardid) {
      return data[i][1];  // return the name of the student with matching ID
    }
  }
  return "Unknown";  // if no match is found, return "Unknown"
}


















