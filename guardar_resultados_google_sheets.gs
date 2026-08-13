
function doPost(e) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var data = JSON.parse(e.postData.contents);

    var resumen = ss.getSheetByName("Resumen");
    if (!resumen) {
      resumen = ss.insertSheet("Resumen");
      resumen.appendRow([
        "Fecha y hora","Apellido y nombre","DNI",
        "Unidad 1","Unidad 2","Unidad 3","Unidad 4","Unidad 5",
        "Total","Porcentaje"
      ]);
    }

    var unidades = ["","","","",""];
    (data.resumen_unidades || []).forEach(function(r, i) {
      if (i < 5) unidades[i] = r.Resultado || "";
    });

    resumen.appendRow([
      data.fecha_hora || new Date(),
      data.nombre || "",
      data.dni || "",
      unidades[0], unidades[1], unidades[2], unidades[3], unidades[4],
      (data.total_correctas || 0) + "/" + (data.total_preguntas || 40),
      data.porcentaje || 0
    ]);

    var respuestas = ss.getSheetByName("Respuestas");
    if (!respuestas) {
      respuestas = ss.insertSheet("Respuestas");
      respuestas.appendRow([
        "Fecha y hora","Apellido y nombre","DNI",
        "Unidad","N° pregunta","Pregunta",
        "Respuesta elegida","Respuesta correcta","Resultado"
      ]);
    }

    (data.respuestas || []).forEach(function(r) {
      respuestas.appendRow([
        data.fecha_hora || new Date(),
        data.nombre || "",
        data.dni || "",
        r.unidad || "",
        r.numero_pregunta || "",
        r.pregunta || "",
        r.respuesta_elegida || "",
        r.respuesta_correcta || "",
        r.correcta ? "Correcta" : "Incorrecta"
      ]);
    });

    return ContentService
      .createTextOutput(JSON.stringify({ok:true}))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ok:false,error:String(err)}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
