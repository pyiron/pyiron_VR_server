The old structures, a little modified.They will hopefully (I couldn't test it) produce a job, which can be executed by the Unity program, 
and put it in the Virtual_Atoms_Structures Folder, upon being started. Some structures might not be necessary anymore (PresentationStructure is the default job
in the save Folder, uncalculated_structure is the same and not uncalculaed, because it could raise errors else.

If you try the jobs and want to make them different, you might need to delete the old jobs by calling pr.remove_jobs() before creating the new one.