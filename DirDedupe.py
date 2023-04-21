import os
import hashlib

from tkinter import StringVar, messagebox
import customtkinter
import asyncio

customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class App(customtkinter.CTk):
    def __init__(self, loop):
        super().__init__()
        self.loop = loop
        self.title("DirDedupe")
        self.geometry(f"{640}x{480}")
        self.minsize(480, 240)
        self.grid_rowconfigure((0, 1, 2, 3), weight=0)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        dir1_sv = StringVar()
        dir1_sv.trace("w", lambda name, index, mode, sv=dir1_sv: self.dir_entry_sv_command(sv))
        self.dir1_entry = customtkinter.CTkEntry(master=self, textvariable=dir1_sv, placeholder_text="Directory Path")
        self.dir1_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        dir2_sv = StringVar()
        dir2_sv.trace("w", lambda name, index, mode, sv=dir2_sv: self.dir_entry_sv_command(sv))
        self.dir2_entry = customtkinter.CTkEntry(master=self, textvariable=dir2_sv, placeholder_text="Directory Path")
        self.dir2_entry.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="ew")
        self.compare_dir1_progress = customtkinter.CTkProgressBar(master=self)
        self.compare_dir1_progress.set(0.0)
        self.compare_dir1_progress.grid(row=1, column=0, padx=(10, 5), sticky="ew")
        self.compare_dir2_progress = customtkinter.CTkProgressBar(master=self)
        self.compare_dir2_progress.set(0.0)
        self.compare_dir2_progress.grid(row=1, column=1, padx=(5, 10), sticky="ew")
        self.compare_progress_label = customtkinter.CTkLabel(master=self, text="")
        self.compare_progress_label.grid(row=2, column=0, columnspan=2)
        self.compare_button = customtkinter.CTkButton(master=self, text="Compare Directories", state="disabled", command=self.compare_button_command)
        self.compare_button.grid(row=3, column=0, columnspan=2)

        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nesw")
        
        self.tabview.add("Mutual Files")
        mutual_tab = self.tabview.tab("Mutual Files")
        mutual_tab.grid_rowconfigure(0, weight=1)
        mutual_tab.grid_rowconfigure(1, weight=0)
        mutual_tab.grid_columnconfigure((0, 1), weight=1)
        self.duplicates_frame = customtkinter.CTkScrollableFrame(master=mutual_tab)
        self.duplicates_frame.grid_rowconfigure(0, weight=1)
        self.duplicates_frame.grid_columnconfigure((0, 1), weight=1)
        self.duplicates_frame.grid(row=0, column=0, columnspan=2, sticky="nesw")
        self.delete_left_button = customtkinter.CTkButton(master=mutual_tab, text="Delete Duplicate Files From Left", state="disabled", command=self.delete_left_command)
        self.delete_left_button.grid(row=1, column=0, padx=(0,5), pady=(5, 0), sticky="ew")
        self.delete_right_button = customtkinter.CTkButton(master=mutual_tab, text="Delete Duplicate Files From Right", state="disabled", command=self.delete_right_command)
        self.delete_right_button.grid(row=1, column=1, padx=(5, 0), pady=(5, 0), sticky="ew")

        # self.tabview.add("Exclusive Files")
        # exclusive_tab = self.tabview.tab("Exclusive Files")
        # exclusive_tab.grid_rowconfigure(0, weight=1)
        # exclusive_tab.grid_columnconfigure((0, 1), weight=1)
        # self.exclusive_left_frame = customtkinter.CTkScrollableFrame(master=exclusive_tab)
        # self.exclusive_left_frame.grid(row=0, column=0, padx=(0, 5), sticky="nesw")
        # self.exclusive_right_frame = customtkinter.CTkScrollableFrame(master=exclusive_tab)
        # self.exclusive_right_frame.grid(row=0, column=1, padx=(5, 0), sticky="nesw")


    def compare_button_command(self):
        self.loop.run_until_complete(self.find_matching_files(self.dir1_entry.get(), self.dir2_entry.get()))

    def dir_entry_sv_command(self, sv):
        self.compare_button.configure(state="normal" if os.path.isdir(self.dir1_entry.get()) and os.path.isdir(self.dir2_entry.get()) else "disabled")
        self.delete_left_button.configure(state="disabled")
        self.delete_right_button.configure(state="disabled")
        for widget in self.duplicates_frame.winfo_children():
            widget.destroy()
        # for widget in self.exclusive_left_frame.winfo_children():
        #     widget.destroy()
        # for widget in self.exclusive_right_frame.winfo_children():
        #     widget.destroy()

    def delete_command(self, column, dir):
        if not messagebox.askyesno(title='Confirmation',
                          message=f'Are you sure that you want to delete the duplicate files from "{dir}"?'):
            return
        self.dir1_entry.configure(state="disabled")
        self.dir2_entry.configure(state="disabled")
        self.compare_button.configure(state="disabled")
        self.delete_left_button.configure(state="disabled")
        self.delete_right_button.configure(state="disabled")

        for duplicate_frame in self.duplicates_frame.winfo_children():
            for label in duplicate_frame.winfo_children()[column].winfo_children():
                filepath = os.path.join(dir, label.cget("text"))
                while True:
                    try:
                        os.remove(filepath)
                        break
                    except:
                        if not messagebox.askretrycancel(title='Error', message=f'Failed to delete "{filepath}". Try again?'):
                            break
                label.destroy()
                self.update_idletasks()
            duplicate_frame.destroy()

        self.dir1_entry.configure(state="normal")
        self.dir2_entry.configure(state="normal")
        self.compare_button.configure(state="normal")

    def delete_left_command(self):
        self.delete_command(0, self.dir1_entry.get())

    def delete_right_command(self):
        self.delete_command(0, self.dir2_entry.get())

    async def get_md5_for_file(self, path):
        # Open file and compute its MD5 checksum
        with open(path, 'rb') as f:
            md5 = hashlib.md5()
            # TODO: Optionally limit number of chunks to read
            while chunk := f.read(65536):  # read in 64KB chunks
                self.update_idletasks()
                md5.update(chunk)
            return md5.hexdigest()

    async def find_matching_files(self, dir1, dir2):
        self.dir1_entry.configure(state="disabled")
        self.dir2_entry.configure(state="disabled")
        self.compare_dir1_progress.set(0.0)
        self.compare_dir2_progress.set(0.0)
        self.compare_progress_label.configure(text="")
        self.compare_button.configure(state="disabled")
        self.delete_left_button.configure(state="disabled")
        self.delete_right_button.configure(state="disabled")
        for widget in self.duplicates_frame.winfo_children():
            widget.destroy()
        # for widget in self.exclusive_left_frame.winfo_children():
        #     widget.destroy()
        # for widget in self.exclusive_right_frame.winfo_children():
        #     widget.destroy()

        dir1_files = {}
        # dir2_files = {}
        duplicate_frames = {}
        with os.scandir(dir1) as dir1_entries, os.scandir(dir2) as dir2_entries:
            dir1_file_entries = [entry for entry in dir1_entries if entry.is_file()]
            dir2_file_entries = [entry for entry in dir2_entries if entry.is_file()]

            # TODO: Display total file count for each directory

            for i, file in enumerate(dir1_file_entries):
                self.compare_dir1_progress.set(i/len(dir1_file_entries))
                self.compare_progress_label.configure(text=file.name)
                self.update_idletasks()
                md5 = await self.get_md5_for_file(file.path)
                try:
                    dir1_files[md5].append(file)
                except KeyError:
                    dir1_files[md5] = [file]
            self.compare_dir1_progress.set(1.0)
            self.compare_progress_label.configure(text="")

            duplicate_found = False
            for i, file in enumerate(dir2_file_entries):
                self.compare_dir2_progress.set(i/len(dir2_file_entries))
                self.compare_progress_label.configure(text=file.name)
                self.update_idletasks()
                md5 = await self.get_md5_for_file(file.path)
                if md5 in dir1_files:
                    if md5 not in duplicate_frames:
                        duplicate_found = True
                        duplicate_frame = customtkinter.CTkFrame(master=self.duplicates_frame)
                        duplicate_frame.grid_columnconfigure((0, 1), weight=1)
                        duplicate_frame.pack(fill="both", expand=True, pady=(0,2))
                        duplicates_left_frame = customtkinter.CTkFrame(master=duplicate_frame, fg_color="transparent")
                        duplicates_left_frame.grid(row=0, column=0, sticky="nesw", padx=(2, 1), pady=(2, 0))
                        duplicates_right_frame = customtkinter.CTkFrame(master=duplicate_frame, fg_color="transparent")
                        duplicates_right_frame.grid(row=0, column=1, sticky="nesw", padx=(1, 2), pady=(2, 0))
                        duplicate_frames[md5] = (duplicates_left_frame, duplicates_right_frame)
                    (left_frame, right_frame) = duplicate_frames[md5]
                    if len(left_frame.winfo_children()) == 0:
                        for dir1_file in dir1_files[md5]:
                            duplicate_left_label = customtkinter.CTkLabel(master=left_frame, text=dir1_file.name, anchor="w")
                            duplicate_left_label.pack(side="top", fill="x", padx=10)
                    duplicate_right_label = customtkinter.CTkLabel(master=right_frame, text=file.name, anchor="w")
                    duplicate_right_label.pack(side="top", fill="x", padx=10)
                # else:
                #     exclusive_left_label = customtkinter.CTkLabel(master=self.exclusive_left_frame, text=dir1_files[md5].name, anchor="w")
                #     exclusive_left_label.pack(fill="x", padx=10)
            self.compare_dir2_progress.set(1.0)
            self.compare_progress_label.configure(text="")

            self.dir1_entry.configure(state="normal")
            self.dir2_entry.configure(state="normal")
            self.compare_button.configure(state="normal")
            if duplicate_found:
                self.delete_left_button.configure(state="normal")
                self.delete_right_button.configure(state="normal")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = App(loop)
    app.mainloop()
    loop.close()
