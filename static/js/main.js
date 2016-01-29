function run(){
	var resultdiv = document.getElementById("resultdiv");
	var statuslabel = document.getElementById("status");
	var run_btn = document.getElementById("run");
	statuslabel.style.color = "green";
	resultdiv.style.color = "green";
	run_btn.disabled = true;
	statuslabel.innerHTML = "正在运行...";
	$.post('/run',function(data) {
		resultdiv.innerHTML = "";
		result = JSON.parse(data)
		if (result.errorMsg == "running") {
			statuslabel.style.color = "red";
			resultdiv.style.color = "red";
			statuslabel.innerHTML = "失败！";
			resultdiv.innerHTML = "已有任务正在运行";
		}else {
			if (result.result == 1) {
				statuslabel.style.color = "green";
				resultdiv.style.color = "green";
				statuslabel.innerHTML = "成功！";
				result.steps.forEach(function(e){
					resultdiv.innerHTML += e + "<br>";
				})
		
			}else {
				statuslabel.style.color = "red";
				resultdiv.style.color = "red";
				statuslabel.innerHTML = "失败！";
				resultdiv.innerHTML = result.errorMsg;
			}
		}
		run_btn.disabled = "";
	})
}

