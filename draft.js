			$("#task-table").append("<tr id='" + taskKey + "'><td>" + "<input oninput='updateName(this.id)' value='" + taskList.name + "'>" + "</input>" + "</td>" + "<td><input onclick='parentId(this)' onclick='updateStatus(this.id)' type='checkbox' checked></td><td><button onclick='deleteTask(this.id)'>❌</button></td></tr>");
			} else {
			$("#task-table").append("<tr id='" + taskKey + "'><td>" + "<input oninput='updateName(this.id)' value='" + taskList.name + "'>" + "</input>" + "</td>" + "<td><input onclick='parentId(this)' onclick='updateStatus(this.id)' type='checkbox'></td><td><button onclick='deleteTask(this.id)'>❌</button></td></tr>");
			};


			$("#task-table").append("<tr id='" + taskKey + "'><td>" + "<input oninput='updateName(this.id)' id='" + taskKey + "' value='" + taskList.name + "'>" + "</input>" + "</td>" + "<td><input onclick='parentId(this)' onclick='updateStatus(this.id)' type='checkbox' id='" + taskKey + "' checked></td><td><button onclick='deleteTask(this.id)' id='" + taskKey + "'>❌</button></td></tr>");
			} else {
			$("#task-table").append("<tr id='" + taskKey + "'><td>" + "<input oninput='updateName(this.id)' id='" + taskKey + "' value='" + taskList.name + "'>" + "</input>" + "</td>" + "<td><input onclick='parentId(this)' onclick='updateStatus(this.id)' type='checkbox' id='" + taskKey + "'></td><td><button onclick='deleteTask(this.id)' id='" + taskKey + "'>❌</button></td></tr>");
			};