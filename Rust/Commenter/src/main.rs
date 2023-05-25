use std::fs::File;
use std::io::{self, BufRead, BufReader, Write};
use std::path::PathBuf;
use clap::{App, Arg};

fn main() -> io::Result<()> {
    let matches = App::new("commenter")
        .version("1.0")
        .author("Spo0ds")
        .about("Add comments to specific line numbers in a file")
        .arg(
            Arg::with_name("file")
                .value_name("FILE")
                .help("Sets the file to add comments to")
                .required(true)
                .index(1),
        )
        .arg(
            Arg::with_name("line")
                .value_name("LINE")
                .help("Sets the line number to add the comment to")
                .required(true)
                .index(2),
        )
        .arg(
            Arg::with_name("comment")
                .value_name("COMMENT")
                .help("The comment to add")
                .required(true)
                .index(3),
        )
        .get_matches();

    // Retrieve the values provided by the user
    let file_path = PathBuf::from(matches.value_of("file").unwrap());
    let line = matches.value_of("line").unwrap().parse::<usize>().unwrap();
    let comment = matches.value_of("comment").unwrap();

    // Read the file into lines
    let lines = BufReader::new(File::open(&file_path)?)
        .lines()
        .collect::<io::Result<Vec<String>>>()?;

    // Modify the desired line with the comment
    let mut modified_lines = lines.clone();
    if let Some(line_to_modify) = modified_lines.get_mut(line - 1) {
        if line_to_modify.trim().is_empty() {
            *line_to_modify = format!("{} // {}", line_to_modify, comment);
        } else if line_to_modify.trim().starts_with("//") {
            *line_to_modify = format!("// {}", comment);
        } else {
            return Err(io::Error::new(io::ErrorKind::Other, format!("Line contains code: {}", line_to_modify)));
        }
    } else {
        return Err(io::Error::new(io::ErrorKind::NotFound, "Line not found"));
    }

    // Write the modified lines back to the file
    let mut file = File::create(&file_path)?;
    for line in modified_lines {
        writeln!(file, "{}", line)?;
    }
 // code tested
    Ok(())
}
