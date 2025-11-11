use pprof::flamegraph::Options;
use pprof::ProfilerGuard;
use std::fs::File;
use std::thread;
use std::thread::sleep;
use std::time::Duration;
use tracing::warn;

pub fn async_write_profile(seconds: i64, file_path: &str, mut image_width: usize) {
    if seconds <= 0 {
        return;
    }

    let fp;
    if file_path.is_empty() {
        fp = String::from("cpu_profile.html");
    } else if !file_path.ends_with(".html") {
        fp = String::from(file_path) + ".html";
    } else {
        fp = file_path.to_string();
    }
    if image_width <= 0 {
        image_width = 1200;
    }
    match ProfilerGuard::new(100) {
        Err(ex) => {
            warn!("flamegraph new error, {:?}", ex);
        }
        Ok(guard) => {
            thread::spawn(move || {
                sleep(Duration::from_secs(seconds as u64));
                if let Ok(fd) = File::create(fp) {
                    if let Ok(report) = guard.report().build() {
                        let mut options = Options::default();
                        options.image_width = Some(image_width);
                        if let Err(ex) = report.flamegraph_with_options(fd, &mut options) {
                            warn!("flamegraph error, {:?}", ex);
                        }
                    }
                }
            });
        }
    }
}
