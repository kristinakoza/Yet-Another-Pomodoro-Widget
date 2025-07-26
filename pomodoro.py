import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QProgressBar, QMessageBox, QStackedWidget, QLineEdit,
    QListWidget, QDialog, QInputDialog, QListWidgetItem
)
from PyQt6.QtGui import QFont, QPalette, QColor, QBrush, QPixmap
from PyQt6.QtCore import Qt, QTimer, QDate, QSize
from PyQt6.QtWidgets import QStyle
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl


class Goal:
    def __init__(self, name="", target_hours=1, completed_hours=0):
        self.name = name
        self.target_hours = target_hours
        self.completed_hours = completed_hours
        self.last_updated = QDate.currentDate().toString(Qt.DateFormat.ISODate)
    
    def to_dict(self):
        return {
            'name': self.name,
            'target_hours': self.target_hours,
            'completed_hours': self.completed_hours,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data):
        goal = cls(data['name'], data['target_hours'], data['completed_hours'])
        goal.last_updated = data['last_updated']
        return goal

class PomodoroApp(QWidget):

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        background = QPixmap("background.jpg")
        if not background.isNull():
            palette = QPalette()
            palette.setBrush(QPalette.ColorRole.Window, QBrush(background.scaled(self.size())))
            self.setPalette(palette)
        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(background.scaled(self.size())))
        self.setPalette(palette)

        # Create stacked widget for multiple pages
        self.stacked_widget = QStackedWidget()
        
    # Page 0: Timer Page
        self.timer_page = QWidget()
        self.setup_timer_page()
        self.stacked_widget.addWidget(self.timer_page)
    
    # Page 1: Stats Page
        self.stats_page = QWidget()
        self.setup_stats_page()
        self.stacked_widget.addWidget(self.stats_page)
    
    # Page 2: Goals Page
        self.goals_page = QWidget()
        self.setup_goals_page()
        self.stacked_widget.addWidget(self.goals_page)
    
        main_layout.addWidget(self.stacked_widget)
    
    # Navigation buttons - UPDATE THESE CONNECTIONS
        nav_layout = QHBoxLayout()
    
        self.timer_btn = QPushButton("Timer")
        self.timer_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        self.timer_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))  # Timer page is index 0
    
        self.stats_btn = QPushButton("Stats")
        self.stats_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        self.stats_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))  # Stats page is index 1
    
        self.goals_btn = QPushButton("Goals")
        self.goals_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        self.goals_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))  # Goals page is index 2
    
    # Add buttons in desired order
        nav_layout.addWidget(self.timer_btn)
        nav_layout.addWidget(self.stats_btn)
        nav_layout.addWidget(self.goals_btn)
    
    # Add theme button
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        self.theme_btn.clicked.connect(self.toggle_theme)
        nav_layout.addWidget(self.theme_btn)
    
        main_layout.addLayout(nav_layout)
    
        self.apply_theme()

    def toggle_theme(self):
        """Switch between light and dark themes"""
        self.is_dark_mode = not self.is_dark_mode
        self.current_theme = self.dark_theme if self.is_dark_mode else self.light_theme
        self.theme_btn.setText("🌞" if self.is_dark_mode else "🌙")
        self.apply_theme()

    def apply_theme(self):
        """Apply the current theme to all UI elements"""
        theme = self.current_theme
    
    # Main window
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(theme['background']))
        self.setPalette(palette)
    
    # Apply to all labels (including stats page)
        for label in [self.timer_label, self.status_label, self.current_goal_label, 
                 self.goal_progress_label, self.sessions_label,
                 self.total_sessions_label, self.total_hours_label]:
            label.setStyleSheet(f"color: {theme['text']};")
    
    # Button style - removed outline by setting border: none
        button_style = f"""
            QPushButton {{
                background: {theme['button_bg']};
                color: {theme['button_text']};
                border-radius: 5px;
                padding: 8px;
                border: none;
            }}
            QPushButton:pressed {{
                background: {theme['text']};
            }}
        """
    
    # Apply button style to all buttons
        for button in [self.timer_btn, self.stats_btn, self.goals_btn, self.theme_btn,
                  self.play_pause_btn, self.reset_btn, self.goal_select_btn]:
            button.setStyleSheet(button_style)
    
    # Progress bar
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                height: 10px;
                border-radius: 5px;
                background: {theme['progress_bg']};
            }}
            QProgressBar::chunk {{
                background: {theme['progress_chunk']};
                border-radius: 5px;
            }}
        """)
    
    # Goals list
        self.goals_list.setStyleSheet(f"""
            QListWidget {{
                background: {theme['list_bg']};
                border-radius: 10px;
                padding: 10px;
                color: {theme['button_text']};
            }}
        """)
    
    # Goals list
        self.goals_list.setStyleSheet(f"""
            QListWidget {{
                background: {theme['list_bg']};
                border-radius: 10px;
                padding: 10px;
                color: {theme['button_text']};
            }}
        """)

    def setup_timer_page(self):
        layout = QVBoxLayout(self.timer_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Current goal label
        self.current_goal_label = QLabel("Current Goal: " + (self.goals[self.current_goal_index].name if self.goals else "No goals"))
        self.current_goal_label.setFont(QFont("Georgia", 14))
        self.current_goal_label.setStyleSheet("color: #FF6B6B;")
        layout.addWidget(self.current_goal_label)

        # Goal progress
        self.goal_progress_label = QLabel()
        self.update_goal_progress_label()
        self.goal_progress_label.setFont(QFont("Georgia", 12))
        layout.addWidget(self.goal_progress_label)

        # Timer label
        self.timer_label = QLabel("25:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setFont(QFont("Georgia", 72, QFont.Weight.Bold))
        self.timer_label.setStyleSheet("color: #FF6B6B;")
        layout.addWidget(self.timer_label)

        # Status label
        self.status_label = QLabel("Work Time")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Georgia", 18))
        self.status_label.setStyleSheet("color: #FF6B6B;")
        layout.addWidget(self.status_label)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(40, 0, 40, 0)
        
        # Play/Pause button
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_pause_btn.setIconSize(QSize(40, 40))
        self.play_pause_btn.setFixedSize(60, 60)
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background: white; 
                border-radius: 30px;
            }
            QPushButton:pressed {
                background: #e0e0e0;
            }
        """)
        self.play_pause_btn.clicked.connect(self.toggle_timer)
        button_layout.addWidget(self.play_pause_btn)
        
        # Reset button
        self.reset_btn = QPushButton()
        self.reset_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.reset_btn.setIconSize(QSize(40, 40))
        self.reset_btn.setFixedSize(60, 60)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background: white; 
                border-radius: 30px;
            }
            QPushButton:pressed {
                background: #e0e0e0;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_timer)
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)

        # Goal selection
        if self.goals:
            goal_select_layout = QHBoxLayout()
            self.goal_select_btn = QPushButton("Switch Goal")
            self.goal_select_btn.setStyleSheet("font-size: 14px; padding: 8px;")
            self.goal_select_btn.clicked.connect(self.show_goal_selection)
            goal_select_layout.addWidget(self.goal_select_btn)
            layout.addLayout(goal_select_layout)

        # Timer progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, self.work_time)
        self.progress.setValue(self.work_time)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                height: 10px;
                border-radius: 5px;
                background: #f8f0f2;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #f8c8dc, stop:1 #fadadd);
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress)
        
        # Sessions label
        self.sessions_label = QLabel(f"Sessions completed: {self.sessions_completed}")
        self.sessions_label.setFont(QFont("Georgia", 12))
        layout.addWidget(self.sessions_label, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def setup_stats_page(self):
        layout = QVBoxLayout(self.stats_page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📈 Your Statistics")
        title.setFont(QFont("Georgia", 20, QFont.Weight.Bold))
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.total_sessions_label = QLabel(f"Total Pomodoros: {self.sessions_completed}")
        self.total_sessions_label.setFont(QFont("Georgia", 14))
        layout.addWidget(self.total_sessions_label)

        total_hours = sum(g.completed_hours for g in self.goals)
        self.total_hours_label = QLabel(f"Total Hours Focused: {total_hours:.1f}")
        self.total_hours_label.setFont(QFont("Georgia", 14))
        layout.addWidget(self.total_hours_label)

    # Stats will automatically update when theme changes
    # because we included them in apply_theme()

    def setup_goals_page(self):
        layout = QVBoxLayout(self.goals_page)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Your Goals")
        title.setFont(QFont("Georgia", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #FF6B6B;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Goals list
        self.goals_list = QListWidget()
        self.goals_list.setStyleSheet("""
            QListWidget {
                background: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.goals_list.itemDoubleClicked.connect(self.edit_goal_dialog)
        self.update_goals_list()
        layout.addWidget(self.goals_list)

        # Button layout for goal actions
        button_layout = QHBoxLayout()
        
        # Add goal button
        add_btn = QPushButton("Add Goal")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #FF6B6B;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background: #e05a5a;
            }
        """)
        add_btn.clicked.connect(self.add_goal_dialog)
        button_layout.addWidget(add_btn)
        
        # Edit goal button
        edit_btn = QPushButton("Edit Goal")
        edit_btn.setStyleSheet("""
            QPushButton {
                background: #6B8EFF;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background: #5a7ae0;
            }
        """)
        edit_btn.clicked.connect(self.edit_goal_dialog)
        button_layout.addWidget(edit_btn)
        
        # Delete goal button
        delete_btn = QPushButton("Delete Goal")
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #FF6B6B;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background: #e05a5a;
            }
        """)
        delete_btn.clicked.connect(self.delete_goal)
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)

    def add_goal_dialog(self):
        name, ok = QInputDialog.getText(self, 'Add Goal', 'Enter goal name:')
        if ok and name:
            target, ok = QInputDialog.getDouble(
                self, 'Target Hours', 
                'Enter target hours (1-12):', 
                min=1, max=12, decimals=1
            )
            if ok:
            # Create new goal and add it directly
                if len(self.goals) >= 5:
                    QMessageBox.warning(self, "Limit Reached", "You can have maximum 5 goals!")
                    return
                
                new_goal = Goal(name, target)
                self.goals.append(new_goal)
                self.save_goals()
                self.update_goals_list()
            
            # If this is the first goal, set it as current
                if len(self.goals) == 1:
                    self.current_goal_index = 0
                    self.current_goal_label.setText("Current Goal: " + name)
                    self.update_goal_progress_label()

    def add_goal(self, goal):
        """Add an existing Goal object to the list"""
        if len(self.goals) >= 5:
            QMessageBox.warning(self, "Limit Reached", "You can have maximum 5 goals!")
            return
        
        self.goals.append(goal)
        self.save_goals()
        self.update_goals_list()
    
    # If this is the first goal, set it as current
        if len(self.goals) == 1:
            self.current_goal_index = 0
            self.current_goal_label.setText("Current Goal: " + goal.name)
            self.update_goal_progress_label()

    def edit_goal_dialog(self, item=None):
        """Handle both button clicks and double-clicks to edit goals"""
        if not self.goals:
            return
            
        # Determine which goal was selected
        if isinstance(item, QListWidgetItem):
            # Called from double-click
            selected = self.goals_list.row(item)
        else:
            # Called from button click
            selected = self.goals_list.currentRow()
            if selected < 0:
                QMessageBox.warning(self, "No Selection", "Please select a goal to edit")
                return
        
        goal = self.goals[selected]
        
        # Get new name
        new_name, ok = QInputDialog.getText(
            self, 'Edit Goal', 
            'Edit goal name:', 
            text=goal.name
        )
        if not ok or not new_name.strip():
            return
            
        # Get new target
        new_target, ok = QInputDialog.getDouble(
            self, 'Edit Target', 
            'Edit target hours (1-12):', 
            value=goal.target_hours,
            min=1, max=12, decimals=1
        )
        if ok:
            self.edit_goal(selected, new_name, new_target)
    def delete_goal(self):
        if not self.goals:
            return
            
        selected = self.goals_list.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a goal to delete")
            return
            
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Delete goal '{self.goals[selected].name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.goals.pop(selected)
            
            # Update current goal index if needed
            if self.current_goal_index >= len(self.goals):
                self.current_goal_index = max(0, len(self.goals) - 1)
                if self.goals:
                    self.current_goal_label.setText("Current Goal: " + self.goals[self.current_goal_index].name)
                else:
                    self.current_goal_label.setText("Current Goal: No goals")
            
            self.save_goals()
            self.update_goals_list()
            self.update_goal_progress_label()



    def update_goals_list(self):
        self.goals_list.clear()
        for i, goal in enumerate(self.goals):
            item_text = f"{goal.name} - {goal.completed_hours}/{goal.target_hours} hours"
            self.goals_list.addItem(item_text)
            if i == self.current_goal_index:
                self.goals_list.item(i).setBackground(QColor("#f8c8dc"))

    def add_goal(self):
        if len(self.goals) >= 5:
            QMessageBox.warning(self, "Limit Reached", "You can have maximum 5 goals!")
            return
            
        name = self.goal_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Info", "Please enter a goal name!")
            return
            
        try:
            target = float(self.target_hours_input.text())
            if not (1 <= target <= 12):
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a number between 1 and 12 for target hours!")
            return
            
        self.goals.append(Goal(name, target))
        self.save_goals()
        self.update_goals_list()
        self.goal_name_input.clear()
        self.target_hours_input.clear()
        
        # If this is the first goal, set it as current and refresh timer page
        if len(self.goals) == 1:
            self.current_goal_index = 0
            self.stacked_widget.removeWidget(self.timer_page)
            self.timer_page = QWidget()
            self.setup_timer_page()
            self.stacked_widget.insertWidget(0, self.timer_page)
            self.stacked_widget.setCurrentIndex(0)

    def show_goal_selection(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Goal")
        dialog.setFixedSize(300, 300)
        
        layout = QVBoxLayout(dialog)
        
        list_widget = QListWidget()
        for goal in self.goals:
            list_widget.addItem(goal.name)
        layout.addWidget(list_widget)
        
        select_btn = QPushButton("Select")
        select_btn.clicked.connect(lambda: self.select_goal(list_widget.currentRow(), dialog))
        layout.addWidget(select_btn)
        
        dialog.exec()

    def select_goal(self, index, dialog):
        if 0 <= index < len(self.goals):
            self.current_goal_index = index
            self.current_goal_label.setText("Current Goal: " + self.goals[self.current_goal_index].name)
            self.update_goal_progress_label()
            dialog.close()

    def update_goal_progress_label(self):
        if self.goals:
            goal = self.goals[self.current_goal_index]
            self.goal_progress_label.setText(
                f"Progress: {goal.completed_hours:.1f}/{goal.target_hours} hours "
                f"({(goal.completed_hours/goal.target_hours)*100:.1f}%)"
            )
        else:
            self.goal_progress_label.setText("No goals set")

    def check_daily_reset(self):
        today = QDate.currentDate().toString(Qt.DateFormat.ISODate)
        for goal in self.goals:
            if goal.last_updated != today:
                goal.completed_hours = 0
                goal.last_updated = today
        self.save_goals()

    def save_goals(self):
        data = {
            'goals': [goal.to_dict() for goal in self.goals],
            'current_goal_index': self.current_goal_index
        }
        with open('goals.json', 'w') as f:
            json.dump(data, f)

    def load_goals(self):
        if os.path.exists('goals.json'):
            with open('goals.json', 'r') as f:
                data = json.load(f)
                self.goals = [Goal.from_dict(goal_data) for goal_data in data['goals']]
                self.current_goal_index = data.get('current_goal_index', 0)
        else:
            self.goals = []

    # [Rest of your timer methods remain the same...]
    # (toggle_timer, start_timer, pause_timer, reset_timer, countdown, timer_complete, update_display)

    def update_timer(self):
        """Countdown timer that updates every second"""
        if self.current_time > 0:
            self.current_time -= 1
            self.update_display()
        else:
            self.timer_complete()
            self.sound.play()
            if self.is_work:
                QMessageBox.information(self, "Great Job!", "You're doing amazing! Keep going 💪")
            else:
                QMessageBox.information(self, "Nice Break!", "Hope you feel refreshed! 🌟")

    def update_display(self):
        """Update all UI elements with current timer state"""
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
        self.sessions_label.setText(f"Sessions completed: {self.sessions_completed}")
        
        # Update progress bar
        if self.is_work:
            self.progress.setRange(0, self.work_time)
            self.progress.setValue(self.current_time)
        else:
            if self.sessions_completed % 4 == 0:
                self.progress.setRange(0, self.long_break)
            else:
                self.progress.setRange(0, self.short_break)
            self.progress.setValue(self.current_time)
        
        # Update status color
        if self.is_work:
            self.status_label.setStyleSheet(f"color: {self.current_theme['text']};")
        else:
            if self.sessions_completed % 4 == 0:
                self.status_label.setStyleSheet("color: #4CAF50;")  # Green for long break
            else:
                self.status_label.setStyleSheet("color: #64B5F6;")  # Blue for short break

    def toggle_timer(self):
        """Toggle between play and pause states"""
        if not self.is_running:
            self.start_timer()
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.pause_timer()
            QTimer.singleShot(60000, self.check_if_still_paused)
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def start_timer(self):
        """Start the timer"""
        if not self.is_running:
            self.is_running = True
            self.timer.start(1000)  # Update every second

    def pause_timer(self):
        """Pause the timer"""
        self.is_running = False
        self.timer.stop()

    def reset_timer(self):
        """Reset the timer to initial state"""
        self.pause_timer()
        QTimer.singleShot(60000, self.check_if_still_paused)
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        if self.is_work:
            self.current_time = self.work_time
        else:
            if self.sessions_completed % 4 == 0:
                self.current_time = self.long_break
            else:
                self.current_time = self.short_break
        self.update_display()

    def check_if_still_paused(self):
        if not self.is_running:
            QMessageBox.information(self, "Still paused?", "Take a break—but don’t forget to resume!")

    def timer_complete(self):
        """Handle when timer reaches zero"""
        self.pause_timer()
    
        if self.is_work:
            if self.goals:
                self.goals[self.current_goal_index].completed_hours += 25/60
                self.save_goals()
                self.update_goal_progress_label()
        
            self.sessions_completed += 1
        # Update stats labels
            if hasattr(self, 'total_sessions_label'):
                self.total_sessions_label.setText(f"Total Pomodoros: {self.sessions_completed}")
                total_hours = sum(g.completed_hours for g in self.goals)
                self.total_hours_label.setText(f"Total Hours Focused: {total_hours:.1f}")
            if self.sound:
                self.sound.play()
    
    # ... rest of the method ...
            if self.sessions_completed % 4 == 0:
                QMessageBox.information(self, "Time's up!", "Take a long break!")
                self.current_time = self.long_break
            else:
                QMessageBox.information(self, "Time's up!", "Take a short break!")
                self.current_time = self.short_break
            self.is_work = False
            self.status_label.setText("Break Time")
        else:
            QMessageBox.information(self, "Break's over!", "Time to work!")
            self.current_time = self.work_time
            self.is_work = True
            self.status_label.setText("Work Time")
        
        self.update_display()
        self.start_timer()  # Auto-start next session

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Timer")
        self.setFixedSize(600, 700)


    # === Theme initialization ===
        self.light_theme = {
            'background': "#FADADD",
            'text': "#FF6B6B",
            'progress_bg': "#f8f0f2",
            'progress_chunk': "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #f8c8dc, stop:1 #fadadd)",
            'button_bg': "white",
            'button_text': "black",
            'list_bg': "white"
        }

        self.dark_theme = {
            'background': "#2D2D2D",
            'text': "#E91E63",
            'progress_bg': "#1E1E1E",
            'progress_chunk': "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #E91E63, stop:1 #9C27B0)",
            'button_bg': "#424242",
            'button_text': "white",
            'list_bg': "#333333"
        }

        self.current_theme = self.light_theme
        self.is_dark_mode = False

    # === Timer settings ===
        self.work_time = 25 * 60  # 25 minutes in seconds
        self.short_break = 5 * 60
        self.long_break = 15 * 60
        self.current_time = self.work_time
        self.is_work = True
        self.sessions_completed = 0
        self.is_running = False
        self.timer = QTimer(self)
        self.sound = QSoundEffect()
        self.sound.setVolume(0.5)  # 50% volume
        self.sound.setObjectName("timerBeep")
        self.timer.timeout.connect(self.update_timer)

    # === Goals management ===
        self.goals = []
        self.current_goal_index = 0
        self.load_goals()
        self.check_daily_reset()

        self.init_ui()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PomodoroApp()
    window.show()
    sys.exit(app.exec())