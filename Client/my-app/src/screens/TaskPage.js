import React, { useState } from 'react';

function TaskPage({ onLCSToggle, useLCSTest }) {
    const [expandedTasks, setExpandedTasks] = useState([]);

    const tasks = [
        {
            id: 'lcs',
            title: 'LCS Task',
            description: 'This is the description for the LCS Task. It explains how the task works and what is expected.'
        },
        {
            id: 'task2',
            title: 'Task 2',
            description: 'Description for Task 2.'
        },
        // Add more tasks as needed
    ];

    const handleCheckboxChange = (taskId, isChecked) => {
        if (taskId === 'lcs') {
            handleLCSTaskChange(isChecked);
        }

        if (isChecked) {
            setExpandedTasks(prevTasks => [...prevTasks, taskId]);
        } else {
            setExpandedTasks(prevTasks => prevTasks.filter(id => id !== taskId));
        }
    }

    const handleLCSTaskChange = (isChecked) => {
        if (onLCSToggle) {
            onLCSToggle(isChecked);
        }
    }
      
  return (
    <div className="container mt-4">
            {tasks.map(task => (
                <div className="card mb-3" key={task.id}>
                    <div className="card-body">
                        <div className="form-check">
                            <input
                                className="form-check-input"
                                type="checkbox"
                                id={task.id}
                                checked={task.id === 'lcs' ? useLCSTest : undefined} // Set the checked attribute for the lcs task
                                onChange={(e) => handleCheckboxChange(task.id, e.target.checked)}
                            />
                            <label className="form-check-label" htmlFor={task.id}>
                                {task.title} {!expandedTasks.includes(task.id) && '(Expand for description)'}
                            </label>
                        </div>
            {expandedTasks.includes(task.id) && (
              <div className="mt-2">
                <p>{task.description}</p>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default TaskPage;
