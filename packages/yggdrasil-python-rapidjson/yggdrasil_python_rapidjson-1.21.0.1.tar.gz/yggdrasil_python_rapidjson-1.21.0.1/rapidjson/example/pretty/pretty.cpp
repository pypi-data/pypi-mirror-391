// JSON pretty formatting example
// This example can only handle UTF-8. For handling other encodings, see prettyauto example.

#include "yggdrasil_rapidjson/reader.h"
#include "yggdrasil_rapidjson/prettywriter.h"
#include "yggdrasil_rapidjson/filereadstream.h"
#include "yggdrasil_rapidjson/filewritestream.h"
#include "yggdrasil_rapidjson/error/en.h"

using namespace yggdrasil_rapidjson;

int main(int, char*[]) {
    // Prepare reader and input stream.
    Reader reader;
    char readBuffer[65536];
    FileReadStream is(stdin, readBuffer, sizeof(readBuffer));

    // Prepare writer and output stream.
    char writeBuffer[65536];
    FileWriteStream os(stdout, writeBuffer, sizeof(writeBuffer));
    PrettyWriter<FileWriteStream> writer(os);

    // JSON reader parse from the input stream and let writer generate the output.
    if (!reader.Parse<kParseValidateEncodingFlag>(is, writer)) {
        fprintf(stderr, "\nError(%u): %s\n", static_cast<unsigned>(reader.GetErrorOffset()), GetParseError_En(reader.GetParseErrorCode()));
        return 1;
    }

    return 0;
}
